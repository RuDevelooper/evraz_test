from sqlalchemy import select, func

from models import *


def get_statistic_counters():
    counters = {}

    opened_query = select(func.count()).select_from(tickets).where(tickets.c.current_status == 1)
    at_work_query = select(func.count()).select_from(tickets).where(tickets.c.current_status == 2)
    done_query = select(func.count()).select_from(tickets).where(tickets.c.current_status == 3)
    cancelled_query = select(func.count()).select_from(tickets).where(tickets.c.current_status == 4)
    start_end_task_time_query = select(
        tickets.c.status_updated_at, tickets_history.c.updated_at
    ).select_from(
        tickets.join(
            tickets_history, tickets_history.c.ticket == tickets.c.id
        )
    ).where(
        tickets_history.c.status == 2, tickets.c.current_status == 3
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
    sum_intervals = sum([(d1 - d2).seconds for d1, d2 in start_end_task_time])
    quantity = len(start_end_task_time)
    avg = sum_intervals / quantity
    return f'{int(avg // 3600)} ч. {int(avg // 60 % 60)} мин.'
