from flask import Flask, request, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
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


@server.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if list(request.form.values())[0] == '1':
            return redirect(url_for('register'))
        elif list(request.form.values())[0] == '2':
            return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('index.html')


@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        log = request.form['username']
        password = request.form['password']
        con = sqlite3.connect('project.db')
        cur = con.cursor()
        query = f'''SELECT hash_password, is_verified FROM users WHERE login="{log}"'''
        data = cur.execute(query).fetchone()
        con.commit()
        con.close()
        if data[1] == 1:
            if data and bcrypt.check_password_hash(data[0], password):
                return redirect(url_for('home', username=log))
            else:
                return render_template('login.html', response='Вы неправильно ввели имя пользователя/пароль')
        else:
            return redirect(url_for('verify_email', username=log, response='Вы не подтверили почту.'))
    else:
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
    else:
        return render_template('register.html')


@server.route('/home/<username>/', methods=['GET', 'POST'])
def home(username):
    if request.method == 'POST':
        if list(request.form.values())[0] == '1':
            return redirect(url_for('create_task', username=username))
        elif list(request.form.values())[0] == '2':
            return redirect(url_for('view_tasks', username=username))
        elif list(request.form.values())[0] == '3':
            return redirect(url_for('index'))
    else:
        return render_template('home.html')


@server.route('/view_tasks/<username>/', methods=['GET', 'POST'])
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
    else:
        con = sqlite3.connect('project.db')
        cur = con.cursor()
        query = cur.execute(f'''SELECT task, description_task FROM tasks WHERE login="{username}"''').fetchall()
        con.commit()
        con.close()
        return render_template('view_tasks.html', query=query, username=username)


@server.route('/create_task/<username>/', methods=['GET', 'POST'])
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


@server.route('/view_task/<username>/<name_task>/', methods=['GET', 'POST'])
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
            return render_template('view_tasks.html', query=query, username=username)
    else:
        con = sqlite3.connect('project.db')
        cur = con.cursor()
        query = cur.execute(f'''SELECT description_task FROM tasks 
        WHERE login="{username}" and task="{name_task}"''').fetchone()
        return render_template('view_task.html', description_task=query[0], name_task=name_task)


@server.route('/verify_email/<username>/', methods=['GET', 'POST'])
def verify_email(username, response=''):
    if request.method == 'POST':
        token = request.form['confirmationToken']
        con = sqlite3.connect('project.db')
        cur = con.cursor()
        query = cur.execute(f'''SELECT token FROM users WHERE login="{username}"''').fetchone()
        if query[0] == token:
            query = cur.execute(f'''UPDATE users SET is_verified = 1 WHERE login="{username}"''')
            con.commit()
            con.close()
            return redirect(url_for('home', username=username))
        else:
            con.commit()
            con.close()
            return render_template('verify_email.html', response='Вы ввели токен не правильно. Проверьте ещё раз.')
    else:
        return render_template('verify_email.html', response=response)


server.run()