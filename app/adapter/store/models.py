import uuid

from sqlalchemy import (  # noqa: WPS235
    Boolean, Column, DateTime, Enum as SqlAlchemyEnum, ForeignKey, String,
    Table, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

from app.adapter.dto.chat import ChatType

Base = declarative_base()


chat_participants = Table(
    'chat_participants',
    Base.metadata,
    Column('chat_id', UUID(as_uuid=True), ForeignKey('chats.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
)

messages_read = Table(
    'messages_read',
    Base.metadata,
    Column('message_id', UUID(as_uuid=True), ForeignKey('messages.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
)


class BaseMixin:
    id = Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class User(Base, BaseMixin):
    __tablename__ = 'users'

    password_hash = Column('password_hash', String(1024), nullable=False, unique=True)
    username = Column('username', String(50), nullable=False)
    email = Column('email', String(128), nullable=False)

    __table_args__ = (
        UniqueConstraint('username', 'email', name='uix_username_email'),
    )


class Chat(Base, BaseMixin):
    __tablename__ = 'chats'

    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    chat_name = Column('chat_name', String(50), nullable=False)
    chat_type = Column('chat_type', SqlAlchemyEnum(ChatType), nullable=False)

    owner = relationship('User', backref='chats')

    participants = relationship(
        'User',
        secondary=chat_participants,
        backref='joined_chats',
        lazy='selectin',
    )


class UserJwt(BaseMixin, Base):
    __tablename__ = 'users_jwt'

    token = Column('token', String(1024), nullable=False, unique=True)
    never_expired = Column('never_expired', Boolean, default=False, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    owner = relationship('User', backref='tokens')


class Message(Base, BaseMixin):
    __tablename__ = 'messages'

    chat_id = Column(UUID(as_uuid=True), ForeignKey('chats.id'), nullable=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    text = Column('text', Text, nullable=False)

    chat = relationship('Chat', backref='messages')
    sender = relationship('User', backref='messages')

    readers = relationship(
        'User',
        secondary=messages_read,
        backref='read_messages',
        lazy='selectin',
    )
