from sqlalchemy import select, func

from models import *


def get_statistic_counters():
    opened_status = select(statuses.c.id).where(
        statuses.c.title == "Новый"
    ).scalar_subquery()
    at_work_status = select(statuses.c.id).where(
        statuses.c.title == "В работе"
    ).scalar_subquery()
    done_status = select(statuses.c.id).where(
        statuses.c.title == "Завершен"
    ).scalar_subquery()
    cancel_status = select(statuses.c.id).where(
        statuses.c.title == "Отменен"
    ).scalar_subquery()

    counters = {}

    opened_query = select(func.count()).select_from(tickets).where(tickets.c.current_status == opened_status)
    at_work_query = select(func.count()).select_from(tickets).where(tickets.c.current_status == at_work_status)
    done_query = select(func.count()).select_from(tickets).where(tickets.c.current_status == done_status)
    cancelled_query = select(func.count()).select_from(tickets).where(tickets.c.current_status == cancel_status)
    start_end_task_time_query = select(
        tickets.c.status_updated_at, tickets_history.c.updated_at
    ).select_from(
        tickets.join(
            tickets_history, tickets_history.c.ticket == tickets.c.id
        )
    ).where(
        tickets_history.c.status == at_work_status, tickets.c.current_status == done_status
    )

    with engine.begin() as connection:
        opened = connection.execute(opened_query).fetchone()[0]
        at_work = connection.execute(at_work_query).fetchone()[0]
        done = connection.execute(done_query).fetchone()[0]
        cancelled = connection.execute(cancelled_query).fetchone()[0]
        start_end_task_time = connection.execute(start_end_task_time_query).fetchall()

    counters.update(
        {
            'opened': opened,
            'at_work': at_work,
            'done': done,
            'cancelled': cancelled,
            'average_time': get_average_interval(start_end_task_time),
        }
    )
    return counters


def get_average_interval(start_end_task_time: list):
    sum_intervals = sum([(t1 - t2).seconds for t1, t2 in start_end_task_time])
    quantity = len(start_end_task_time)
    avg = sum_intervals / quantity
    return f'{int(avg // 3600)} ч. {int(avg // 60 % 60)} мин.'
