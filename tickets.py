from sqlalchemy import select, join

from models import *


def create_new_ticket(task_description):
    insert = tickets.insert().values(description=task_description)
    engine.execute(insert)


def get_opened_tasks():
    query = select(tickets).select_from(
        tickets.join(
            statuses,
            tickets.c.current_status == statuses.c.id
        )
    ).where(
        statuses.c.title == "Новый"
    )
    tickets_list = engine.execute(query).fetchall()
    tickets_dict = []
    for t in tickets_list:
        print(t)
        tickets_dict.append(
            {
                'id': t[0],
                'description': t[1],
                'created_at': t[2],
                'user_id': t[3],
                'current_status': t[4],
                'status_updated_at': t[5],
            }
        )

    return tickets_dict


def get_user_tasks(user_id):
    query = select(tickets).select_from(
        tickets.join(
            statuses,
            tickets.c.current_status == statuses.c.id
        )
    ).where(
        statuses.c.title == "В работе",
        tickets.c.user_id == user_id
    )
    tickets_list = engine.execute(query).fetchall()
    tickets_dict = []
    for t in tickets_list:
        print(t)
        tickets_dict.append(
            {
                'id': t[0],
                'description': t[1],
                'created_at': t[2],
                'user_id': t[3],
                'current_status': t[4],
                'status_updated_at': t[5],
            }
        )

    return tickets_dict


def add_to_my_tickets(ticket_id, user_id):
    now = datetime.now()
    status = 2

    query = tickets.update().values({
        tickets.c.user_id: user_id,
        tickets.c.current_status: status,
        tickets.c.status_updated_at: now
    }).where(tickets.c.id == ticket_id)

    insert = tickets_history.insert().values(
        status=status,
        ticket=ticket_id,
        updated_at=now,
        updated_by=user_id,
    )

    with engine.begin() as connection:
        connection.execute(insert)
        connection.execute(query)
