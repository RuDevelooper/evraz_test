from flask import Flask, render_template, request, make_response, redirect

from models import *
from auth import auth, check_auth
from tickets import create_new_ticket, add_to_my_tickets, get_opened_tasks, get_user_tasks

app = Flask(__name__)


@app.before_first_request
async def startup():
    # соединение с БД перед выполнением запросов
    engine.connect()


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        login = request.form.get('login')
        password = request.form.get('password')
        auth_status = auth(login, password)

        if auth_status['status']:
            response = redirect('/')
            response.set_cookie('authenticated_user', auth_status['user_id'])
        else:
            response = make_response(render_template('login.html', message='Проверьте имя пользователя и пароль'))

        return response

    if request.method == "GET":
        response = make_response(render_template('login.html'))
        response.delete_cookie('is_authenticated')
        return response


@app.route('/', methods=['GET', 'POST'])
@check_auth
def main(user):
    if request.method == "GET":
        tickets = get_opened_tasks()
        return render_template(
            "index.html",
            user=user,
            tickets=tickets
        )

    if request.method == "POST":
        ticket = request.form.get('ticket')
        add_to_my_tickets(ticket, user['id'])
        return redirect('/')

@app.route('/my_tasks/', methods=['GET', 'POST'])
@check_auth
def my_tasks(user):
    if request.method == "GET":
        tickets = get_user_tasks(user['id'])
        return render_template(
            "my_tasks.html",
            user=user,
            tickets=tickets
        )

    if request.method == "POST":
        ticket = request.form.get('ticket')
        # add_to_my_tickets(ticket, user['id'])
        return redirect('/my_tasks/')

@app.route('/at_work/', methods=['GET', 'POST'])
@check_auth
def at_work(user):
    if request.method == "GET":
        tickets = get_user_tasks(user['id'])
        return render_template(
            "at_work.html",
            user=user,
            tickets=tickets
        )

    if request.method == "POST":
        ticket = request.form.get('ticket')
        # add_to_my_tickets(ticket, user['id'])
        return redirect('/my_tasks/')

@app.route('/new_task/', methods=['GET', 'POST'])
@check_auth
def new_task(user):
    if request.method == "GET":
        print(user)
        return render_template("new_task.html", user=user)

    if request.method == "POST":
        task_description = request.form.get('task_description')
        create_new_ticket(task_description)
        return redirect('/')


if __name__ == '__main__':
    app.run()
