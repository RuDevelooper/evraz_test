from flask import Flask, render_template, request, make_response, redirect

from services.lib import get_all_users_and_statuses
from models import *
from services.auth import auth, check_auth
from services.statistic import get_statistic_counters
from services.tickets import (
    create_new_ticket,
    get_opened_tickets,
    get_user_tickets,
    change_ticket_status,
    get_tickets_at_work,
    get_at_work_ticket_history,
    get_archive_tickets,
    get_archive_ticket_history
)

app = Flask(__name__)


@app.before_first_request
def startup():
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
        tickets = get_opened_tickets()
        return render_template(
            "index.html",
            user=user,
            tickets=tickets
        )

    if request.method == "POST":
        ticket = request.form.get('ticket')
        change_ticket_status(ticket, user['id'], "В работе")
        return redirect('/')


@app.route('/my_tickets/', methods=['GET', 'POST'])
@check_auth
def my_tickets(user):
    if request.method == "GET":
        tickets = get_user_tickets(user['id'])
        return render_template(
            "my_tickets.html",
            user=user,
            tickets=tickets
        )


@app.route('/at_work/', methods=['GET'])
@check_auth
def at_work(user):
    if request.method == "GET":
        tickets = get_tickets_at_work()
        history = get_at_work_ticket_history()
        lib = get_all_users_and_statuses()
        return render_template(
            "at_work.html",
            user=user,
            tickets=tickets,
            history=history,
            users=lib.get('users'),
            statuses=lib.get('statuses'),
        )


@app.route('/archive/', methods=['GET'])
@check_auth
def archive(user):
    if request.method == "GET":
        tickets = get_archive_tickets()
        history = get_archive_ticket_history()
        lib = get_all_users_and_statuses()
        return render_template(
            "archive.html",
            user=user,
            tickets=tickets,
            history=history,
            users=lib.get('users'),
            statuses=lib.get('statuses'),
        )


@app.route('/statistic/', methods=['GET'])
@check_auth
def statistic(user):
    if request.method == "GET":
        counters = get_statistic_counters()
        return render_template(
            "statistic.html",
            user=user,
            counters=counters
        )


@app.route('/new_ticket/', methods=['GET', 'POST'])
@check_auth
def new_ticket(user):
    if request.method == "GET":
        return render_template("new_ticket.html", user=user)

    if request.method == "POST":
        ticket_description = request.form.get('ticket_description')
        create_new_ticket(ticket_description)
        return redirect('/')


@app.route('/cancel_ticket/', methods=['POST', ])
@check_auth
def cancel_ticket(user):
    if request.method == "POST":
        ticket = request.form.get('ticket')
        change_ticket_status(ticket, user['id'], "Отменен")
        return redirect('/my_tickets/')


@app.route('/finish_ticket/', methods=['POST', ])
@check_auth
def finish_ticket(user):
    if request.method == "POST":
        ticket = request.form.get('ticket')
        change_ticket_status(ticket, user['id'], "Завершен")
        return redirect('/my_tickets/')


if __name__ == '__main__':
    app.run()
