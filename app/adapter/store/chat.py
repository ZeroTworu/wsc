from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import insert, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from starlette import status

from app.adapter.dto.chat import ChatDto
from app.adapter.store.models import Chat, chat_participants, User

if TYPE_CHECKING:
    from typing import List
    from uuid import UUID

    from app.adapter.dto.chat import ChatCreateDto
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
                .outerjoin(chat_participants, Chat.id == chat_participants.c.chat_id)
                .options(selectinload(Chat.participants))
                .where(
                    or_(
                        Chat.owner_id == user_id,
                        chat_participants.c.user_id == user_id,
                    )
                )
            )
            chats = result.scalars().unique().all()
            return [ChatDto.model_validate(chat) for chat in chats]

    async def get_all_chats(self: 'DataBaseAdapter') -> 'List[ChatDto]':
        async with self._sc() as session:
            result = await session.execute(
                select(Chat).options(selectinload(Chat.participants))
            )
            chats = result.scalars().all()
            return [ChatDto.model_validate(chat) for chat in chats]

    async def get_chat_by_id(self: 'DataBaseAdapter', chat_id: 'UUID') -> 'ChatDto|None':
        async with self._sc() as session:
            result = await session.execute(
                select(Chat)
                .options(selectinload(Chat.participants))
                .where(Chat.id == chat_id)
            )
            chat = result.scalar_one_or_none()
            if chat is None:
                return None
            return ChatDto.model_validate(chat)

    async def get_chat_by_id_and_user_id(self: 'DataBaseAdapter', chat_id: 'UUID', user_id: 'UUID') -> 'ChatDto|None':
        async with self._sc() as session:
            result = await session.execute(
                select(Chat)
                .options(selectinload(Chat.participants))
                .where(
                    Chat.id == chat_id,
                    or_(
                        Chat.owner_id == user_id,
                        Chat.participants.any(id=user_id)
                    )
                )
            )

            if (chat := result.scalar_one_or_none()) is not None:  # noqa: WPS332
                return ChatDto.model_validate(chat, from_attributes=True)

    async def leave_chat(self: 'DataBaseAdapter', chat_id: 'UUID', user_id: 'UUID') -> 'bool':
        async with self._sc() as session:
            chat = await session.get(Chat, chat_id)
            user = await session.get(User, user_id)

            if chat is None or user is None:
                return False

            if user not in chat.participants:
                return False

            if chat.owner_id == user_id:
                chat.participants.clear()
                await session.delete(chat)
                await session.commit()
                return True

            chat.participants.remove(user)
            await session.commit()
            return True
