from sqlalchemy import select, or_

from models import *


def create_new_ticket(task_description):
    insert = tickets.insert().values(description=task_description)
    engine.execute(insert)


def get_opened_tickets():
    query = select(tickets).select_from(
        tickets.join(
            statuses,
            tickets.c.current_status == statuses.c.id
        )
    ).where(
        statuses.c.title == "Новый"
    )
    tickets_list = engine.execute(query).fetchall()
    return parse_tickets(tickets_list)


def get_user_tickets(user_id):
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
    return parse_tickets(tickets_list)


def get_tickets_at_work():
    query = select(tickets).select_from(
        tickets.join(
            statuses,
            tickets.c.current_status == statuses.c.id
        )
    ).where(
        statuses.c.title == "В работе",
    )

    tickets_list = engine.execute(query).fetchall()
    return parse_tickets(tickets_list)


def get_at_work_ticket_history():
    status_id = select(statuses.c.id).where(
        statuses.c.title == "В работе"
    ).scalar_subquery()

    tickets_history_query = select(tickets_history).select_from(
        tickets.join(tickets_history, tickets.c.id == tickets_history.c.ticket)
    ).where(tickets.c.current_status == status_id)

    tickets_history_list = engine.execute(tickets_history_query).fetchall()

    return parse_tickets_history(tickets_history_list)


def get_archive_tickets():
    query = select(tickets).select_from(
        tickets.join(
            statuses,
            tickets.c.current_status == statuses.c.id
        )
    ).where(
        or_(statuses.c.title == "Отменен", statuses.c.title == "Завершен")
    )

    tickets_list = engine.execute(query).fetchall()
    return parse_tickets(tickets_list)


def get_archive_ticket_history():
    done_status = select(statuses.c.id).where(
        statuses.c.title == "Завершен"
    ).scalar_subquery()
    cancel_status = select(statuses.c.id).where(
        statuses.c.title == "Отменен"
    ).scalar_subquery()

    tickets_history_query = select(tickets_history).select_from(
        tickets.join(tickets_history, tickets.c.id == tickets_history.c.ticket)
    ).where(
        or_(
            tickets.c.current_status == done_status,
            tickets.c.current_status == cancel_status)
    )

    tickets_history_list = engine.execute(tickets_history_query).fetchall()

    return parse_tickets_history(tickets_history_list)


def change_ticket_status(ticket_id, user_id, status: str):
    now = datetime.now()
    status_id = select(statuses.c.id).where(statuses.c.title == status).scalar_subquery()

    query = tickets.update().values({
        tickets.c.user_id: user_id,
        tickets.c.current_status: status_id,
        tickets.c.status_updated_at: now
    }).where(tickets.c.id == ticket_id)

    insert = tickets_history.insert().values(
        status=status_id,
        ticket=ticket_id,
        updated_at=now,
        updated_by=user_id,
    )

    with engine.begin() as connection:
        connection.execute(insert)
        connection.execute(query)


def parse_tickets(tickets_list):
    tickets = []
    for t in tickets_list:
        tickets.append(
            {
                'id': t[0],
                'description': t[1],
                'created_at': t[2],
                'user_id': t[3],
                'current_status': t[4],
                'status_updated_at': t[5],
            }
        )
    return tickets


def parse_tickets_history(tickets_history_list: list):
    history = {}
    for h in tickets_history_list:
        if history.get(h[2]):
            history.get(h[2]).append(
                {
                    'id': h[0],
                    'status': h[1],
                    'ticket': h[2],
                    'updated_at': h[3],
                    'updated_by': h[4],
                }
            )
        else:
            history.update({
                h[2]: [
                    {
                        'id': h[0],
                        'status': h[1],
                        'ticket': h[2],
                        'updated_at': h[3],
                        'updated_by': h[4],
                    },
                ]
            })

    return history
