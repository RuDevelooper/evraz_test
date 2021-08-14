from functools import wraps

from flask import request
from sqlalchemy import select
from werkzeug.utils import redirect

from models import users, engine


def auth(login, password):
    auth_status = {
        'status': False,
    }
    user = select(users).where(users.c.login == login)
    result = engine.execute(user)

    if result.first():
        user_password = engine.execute(select(users.c.password).where(users.c.login == login))
        if user_password.fetchone()[0] == password:
            auth_status['status'] = True
            user_id = engine.execute(select(users.c.id).where(users.c.login == login)).fetchone()[0]
            auth_status.update(
                {'user_id': str(user_id)}
            )

    return auth_status


def check_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.cookies.get('authenticated_user'):
            return redirect('/login/')
        else:
            user_info = engine.execute(select(users).where(users.c.id == request.cookies.get('authenticated_user'))).fetchone()
            user = {
                'id': user_info[0],
                'login': user_info[1],
                'fullname': user_info[3],
            }
            return func(*args, user=user, **kwargs)
    return wrapper