from sqlalchemy import select, join

from models import *


def get_all_users_and_statuses():
    users_query = select(users)
    statuses_query = select(statuses)

    with engine.begin() as connection:
        users_list = connection.execute(users_query).fetchall()
        statuses_list = connection.execute(statuses_query).fetchall()

    users_dict = {}
    statuses_dict = {}

    for (id, login, password, fullname) in users_list:
        print(id)
        print(fullname)
        users_dict.update(
            {id: fullname}
        )
    for (id, title) in statuses_list:
        statuses_dict.update(
            {id: title}
        )

    return {
        'users': users_dict,
        'statuses': statuses_dict,
    }

