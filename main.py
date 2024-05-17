from flask import Flask, request, render_template, redirect, url_for
import sqlite3


server = Flask(__name__)


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
        print(request.form['username'], request.form['password'])
        query = f'''SELECT * FROM users WHERE login = "{log}" AND password = "{password}"'''
        data = cur.execute(query).fetchall()
        con.commit()
        con.close()
        if data:
            return redirect(url_for('home', username=log))
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')


@server.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        log = request.form['username']
        password = request.form['password']
        con = sqlite3.connect('project.db')
        cur = con.cursor()
        query = cur.execute(f'''SELECT login FROM users WHERE login = "{log}"''').fetchall()
        if len(query) == 1:
            con.close()
            return {'anwser': 'Такой пользователь уже существует.'}
        else:
            query = f'''INSERT INTO users (login, password) VALUES ("{log}", 
            "{password}")'''
            cur.execute(query)
            con.commit()
            con.close()
            return redirect(url_for('home', username=log))
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


server.run()