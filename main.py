from flask import Flask, request, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
import secrets
import datetime


server = Flask(__name__)
bcrypt = Bcrypt(server)
server.config['SECRET_KEY'] = secrets.token_urlsafe(32)
server.config['MAIL_SERVER'] = 'smtp.yandex.ru'
server.config['MAIL_PORT'] = 465
server.config['MAIL_USE_SSL'] = True
server.config['MAIL_USERNAME'] = 'task.tracker.2024@yandex.ru'
server.config['MAIL_PASSWORD'] = 'sbibgayalkjxdyou'
mail = Mail(server)
login_manager = LoginManager(server)
login_manager.login_view = '/'


@login_manager.user_loader
def load_user(id):
    con = sqlite3.connect('project.db')
    cur = con.cursor()
    query = cur.execute(f'''SELECT login, hash_password FROM users WHERE id="{id}"''').fetchone()
    con.close()
    return User(id, query[0], query[1])


class User(UserMixin):
    def __init__(self, id, username, hash_password):
        self.id = id
        self.username = username
        self.hash_password = hash_password

    def get_id(self):
        return self.id


@server.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if list(request.form.values())[0] == '1':
            return redirect(url_for('register'))
        elif list(request.form.values())[0] == '2':
            return redirect(url_for('login'))
    return render_template('index.html')


@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        log = request.form['username']
        password = request.form['password']
        con = sqlite3.connect('project.db')
        cur = con.cursor()
        query = f'''SELECT id, hash_password, is_verified FROM users WHERE login="{log}"'''
        data = cur.execute(query).fetchone()
        if data[2] == 1:
            if data and bcrypt.check_password_hash(data[1], password):
                query = cur.execute(f'''SELECT id, hash_password FROM users WHERE login="{log}"''').fetchone()
                user = User(query[0], log, query[1])
                login_user(user)
                con.commit()
                con.close()
                return redirect(url_for('home', username=log))
            con.commit()
            con.close()
            return render_template('login.html', response='Вы неправильно ввели имя пользователя/пароль')
        return redirect(url_for('verify_email', username=log, response='Вы не подтверили почту.'))
    return render_template('login.html')


@server.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        log = request.form['username']
        password = request.form['password']
        con = sqlite3.connect('project.db')
        cur = con.cursor()
        query = cur.execute(f'''SELECT login FROM users WHERE login="{log}"''').fetchall()
        query_sec = cur.execute(f'''SELECT email FROM users WHERE email="{email}"''').fetchall()
        if len(list(query)) >= 1 or len(list(query_sec)) >= 1:
            con.close()
            return render_template('register.html', response='Пользователь с таким именем '
                                                             'или адресом электронной почты уже существует')
        else:
            token = secrets.token_urlsafe(32)
            msg = Message(f'Confirm your mail for Task Tracker! Your code : {token}',
                          sender='task.tracker.2024@yandex.ru', recipients=[email])
            mail.send(msg)
            query = f'''INSERT INTO users (login, hash_password, token, is_verified, email) VALUES ("{log}", 
            "{bcrypt.generate_password_hash(password).decode("utf-8")}", "{token}", "{0}", "{email}")'''
            cur.execute(query)
            con.commit()
            con.close()
            return redirect(url_for('verify_email', username=log))
    return render_template('register.html')


@server.route('/home/<username>/', methods=['GET', 'POST'])
@login_required
def home(username):
    if request.method == 'POST':
        if list(request.form.values())[0] == '1':
            return redirect(url_for('create_task', username=username))
        elif list(request.form.values())[0] == '2':
            return redirect(url_for('view_tasks', username=username))
        elif list(request.form.values())[0] == '3':
            logout_user()
            return redirect(url_for('index'))
    return render_template('home.html', username=username)


@server.route('/view_tasks/<username>', methods=['GET', 'POST'])
@login_required
def view_tasks(username):
    if request.method == 'POST':
        if list(request.form.values())[1] == '1':
            return redirect(url_for('view_task', username=username, name_task=list(request.form.values())[0]))
        elif list(request.form.values())[1] == '2':
            con = sqlite3.connect('project.db')
            cur = con.cursor()
            query = cur.execute(f'''DELETE FROM tasks WHERE login="{username}" 
            AND task="{list(request.form.values())[0]}"''')
            query = cur.execute(f'''SELECT task, description_task FROM tasks WHERE login="{username}"''').fetchall()
            con.commit()
            con.close()
            return render_template('view_tasks.html', query=query, username=username)
        elif list(request.form.values())[1] == '3':
            return redirect(url_for('home', username=username))
    con = sqlite3.connect('project.db')
    cur = con.cursor()
    query = cur.execute(f'''SELECT task, description_task FROM tasks WHERE login="{username}"''').fetchall()
    con.close()
    return render_template('view_tasks.html', query=query, username=username)


@server.route('/create_task/<username>', methods=['GET', 'POST'])
@login_required
def create_task(username):
    if request.method == 'POST':
        name_task = request.form['taskName']
        description_task = request.form['taskDescription']
        con = sqlite3.connect('project.db')
        cur = con.cursor()
        cur.execute(f'''INSERT INTO tasks VALUES ("{username}", "{name_task}", "{description_task}")''')
        con.commit()
        con.close()
        return redirect(url_for('view_task', username=username, name_task=name_task))
    else:
        return render_template('create_task.html')


@server.route('/view_task/<username>/<name_task>', methods=['GET', 'POST'])
@login_required
def view_task(username, name_task):
    if request.method == 'POST':
        if list(request.form.values())[0] == '1':
            return redirect(url_for('view_tasks', username=username))
        elif list(request.form.values())[1] == '2':
            con = sqlite3.connect('project.db')
            cur = con.cursor()
            query = cur.execute(f'''DELETE FROM tasks WHERE login="{username}" 
            AND task="{list(request.form.values())[0]}"''')
            query = cur.execute(f'''SELECT task, description_task FROM tasks WHERE login="{username}"''').fetchall()
            con.commit()
            con.close()
            return redirect(url_for('view_tasks.html', query=query, username=username))
    con = sqlite3.connect('project.db')
    cur = con.cursor()
    query = cur.execute(f'''SELECT description_task FROM tasks 
    WHERE login="{username}" and task="{name_task}"''').fetchone()
    return render_template('view_task.html', description_task=query[0], name_task=name_task)


@server.route('/verify_email/<username>', methods=['GET', 'POST'])
def verify_email(username, response=''):
    if request.method == 'POST':
        token = request.form['confirmationToken']
        con = sqlite3.connect('project.db')
        cur = con.cursor()
        query = cur.execute(f'''SELECT token FROM users WHERE login="{username}"''').fetchone()
        if query[0] == token:
            query = cur.execute(f'''UPDATE users SET is_verified = 1 WHERE login="{username}"''')
            query = cur.execute(f'''SELECT id, hash_password FROM users WHERE login="{username}"''').fetchone()
            user = User(query[0], username, query[1])
            login_user(user)
            con.commit()
            con.close()
            return redirect(url_for('home', username=username))
        con.commit()
        con.close()
        return render_template('verify_email.html', response='Вы ввели токен не правильно. Проверьте ещё раз.')
    return render_template('verify_email.html', response=response)


server.run()