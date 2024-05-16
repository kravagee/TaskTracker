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
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        print(request.form['username'], request.form['password'])
        query = f'''SELECT * FROM users WHERE login = "{log}" AND password = "{password}"'''
        data = cur.execute(query).fetchall()
        if data:
            return redirect(url_for('home'))
        else:
            return {'anwser': 'Ошибка. Неверный логин/пароль.'}
    else:
        return render_template('login.html')


@server.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        log = request.form['username']
        password = request.form['password']
        con = sqlite3.connect('users.db')
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
            return redirect(url_for('home'))
    else:
        return render_template('register.html')


@server.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if list(request.form.values())[0] == '1':
            return redirect(url_for('create_projects'))
        elif list(request.form.values())[0] == '2':
            return redirect(url_for('view_projects'))
    else:
        return render_template('home.html')

server.run()