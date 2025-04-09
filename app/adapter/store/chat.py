from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from starlette import status

from app.adapter.dto import ChatDto
from app.adapter.store.models import Chat, chat_participants

if TYPE_CHECKING:
    from typing import List
    from uuid import UUID

    from app.adapter.dto import ChatCreateDto
    from app.adapter.store.sql_adapter import DataBaseAdapter


class ChatAdapter:
    async def create_chat(
        self: 'DataBaseAdapter',
        owner_id: 'UUID',
        chat: 'ChatCreateDto',
    ) -> 'ChatDto':
        async with self._sc() as session:
            created_chat = Chat(
                owner_id=owner_id,
                chat_name=chat.chat_name,
                chat_type=chat.chat_type,
            )
            session.add(created_chat)
            await session.flush()

            all_participants = set(chat.participants + [owner_id])
            values = [{'chat_id': created_chat.id, 'user_id': uid} for uid in all_participants]
            try:
                await session.execute(insert(chat_participants), values)
            except IntegrityError as exc:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail='One or more user IDs do not exist or are invalid.',
                ) from exc

            await session.commit()
            await session.refresh(created_chat)
            return ChatDto.model_validate(created_chat)

    async def get_my_chats(self: 'DataBaseAdapter', user_id: 'UUID') -> 'List[ChatDto]':
        async with self._sc() as session:
            result = await session.execute(
                select(Chat)
                .join(chat_participants)
                .where(chat_participants.c.user_id == user_id)
                .options(selectinload(Chat.participants))
            )
            chats = result.scalars().all()
            return [ChatDto.model_validate(chat) for chat in chats]

    async def get_all_chats(self: 'DataBaseAdapter') -> 'List[ChatDto]':
        async with self._sc() as session:
            result = await session.execute(
                select(Chat).options(selectinload(Chat.participants))
            )
            chats = result.scalars().all()
            return [ChatDto.model_validate(chat) for chat in chats]
