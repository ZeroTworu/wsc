from typing import TYPE_CHECKING

from fastapi import WebSocketException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import selectinload
from starlette import status

from app.adapter.dto.chat import (
    ChatHistoryMessageDto, ChatMessageCreateDto, ChatMessageDto,
)
from app.adapter.store.models import Chat, Message, User, chat_participants

if TYPE_CHECKING:
    from typing import List
    from uuid import UUID

    from app.adapter.store.sql_adapter import DataBaseAdapter


class MessageAdapter:
    async def save_message(
        self: 'DataBaseAdapter',
        msg: 'ChatMessageCreateDto',
    ) -> 'ChatMessageDto':
        async with self._sc() as session:
            m_message = Message(
                sender_id=msg.sender_id,
                chat_id=msg.chat_id,
                text=msg.text,
            )
            session.add(m_message)
            await session.commit()
            await session.refresh(
                m_message,
                attribute_names=['readers', 'created_at', 'updated_at'],
            )

            return ChatMessageDto.model_validate(m_message)

    async def get_chat_messages_by_chat_and_user_id(
            self: 'DataBaseAdapter',
            chat_id: 'UUID',
            user_id: 'UUID',
            offset: int = 0,
            limit: int = 5,
    ) -> 'List[ChatHistoryMessageDto]':
        async with self._sc() as session:
            is_participant_subquery = select(chat_participants.c.chat_id).where(
                and_(
                    chat_participants.c.chat_id == chat_id,
                    chat_participants.c.user_id == user_id
                )
            ).exists()

            query = (
                select(Message)
                .join(Chat)
                .options(
                    selectinload(Message.readers),
                    selectinload(Message.sender),
                    selectinload(Message.chat).selectinload(Chat.participants),
                )
                .where(
                    Message.chat_id == chat_id,
                    or_(
                        Chat.owner_id == user_id,
                        is_participant_subquery
                    )
                )
                .offset(offset)
                .limit(limit)
            )

            result = await session.execute(query)
            messages = result.scalars().all()
            return [ChatHistoryMessageDto.model_validate(msg) for msg in messages]

    async def add_reader(
        self: 'DataBaseAdapter',
        chat_id: 'UUID',
        message_id: 'UUID',
        user_id: 'UUID',
    ) -> 'ChatMessageDto':
        async with self._sc() as session:
            stmt = (
                select(Message)
                .join(Message.chat)
                .options(
                    selectinload(Message.readers),
                    selectinload(Message.chat).selectinload(Chat.participants)
                )
                .where(
                    Message.id == message_id,
                    Message.chat_id == chat_id,
                    or_(
                        Chat.owner_id == user_id,
                        Chat.participants.any(id=user_id)
                    )
                )
            )
            result = await session.execute(stmt)
            message = result.scalar_one_or_none()
            if message is None:
                raise WebSocketException(
                    code=status.WS_1003_UNSUPPORTED_DATA,
                    reason='Message not in chat or user not a participant',
                )

            user = await session.get(User, user_id)
            message.readers.append(user)

            await session.commit()
            await session.refresh(message)

            return ChatMessageDto.model_validate(message, from_attributes=True)
