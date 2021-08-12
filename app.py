from urllib import response

from flask import Flask, render_template, request, make_response, redirect, flash
from sqlalchemy import func
from sqlalchemy.sql import select, exists
from models import *

app = Flask(__name__)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":

        login = request.form.get('login')
        password = request.form.get('password')
        user = select(users).where(users.c.login == login)
        connect = engine.connect()
        result = connect.execute(user)
        if result.first():
            user_password = connect.execute(select(users.c.password).where(users.c.login == login))
            if user_password.fetchone()[0] == password:
                response = redirect('/')
                response.set_cookie('is_authenticated', 'True', max_age=60 * 60 * 24)
                return response
            else:
                response = make_response(render_template('login.html'))
                response.delete_cookie('is_authenticated')
                return response
        else:
            return render_template('login.html', message='Логин или пароль указаны не верно')

    if request.method == "GET":
        response = make_response(render_template('login.html'))
        response.delete_cookie('is_authenticated')
        return response


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == "GET":
        if request.cookies.get('is_authenticated') == 'True':
            return render_template("index.html")
        else:
            return redirect('/login/')

    if request.method == "POST":
        print(request.form.get('login'))
        print(request.form.get('password'))
    return render_template('login.html')


if __name__ == '__main__':
    app.run()
