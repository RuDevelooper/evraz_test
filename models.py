from datetime import datetime

from sqlalchemy import (
    create_engine,
    DateTime,
    Table,
    Column,
    Integer,
    String,
    MetaData,
    ForeignKey
)

engine = create_engine('sqlite:///project.db', echo=True)

metadata = MetaData()

users = Table(
    'user', metadata,
    Column('id', Integer, primary_key=True),
    Column('login', String, unique=True),
    Column('password', String),
    Column('fullname', String),
)

tickets = Table(
    'ticket', metadata,
    Column('id', Integer, primary_key=True),
    Column('description', String),
    Column('created_at', DateTime, default=datetime.now),
    Column('user_id', None, ForeignKey('user.id')),
    Column('current_status', ForeignKey('status.id'), default=1),
    Column('status_updated_at', DateTime),
)

statuses = Table(
    'status', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
)

tickets_history = Table(
    'ticket_history', metadata,
    Column('id', Integer, primary_key=True),
    Column('status', None, ForeignKey('status.id')),
    Column('ticket', None, ForeignKey('ticket.id')),
    Column('updated_at', DateTime, default=datetime.now),
)

metadata.create_all(engine)
