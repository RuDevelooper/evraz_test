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

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

engine = create_engine('sqlite:///project.db', echo=True)

metadata = MetaData(
    naming_convention=naming_convention
)

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
    Column('updated_by', None, ForeignKey('user.id'), nullable=True),
)

# metadata.create_all(engine)
