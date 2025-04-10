from typing import TYPE_CHECKING

from app.adapter.dto.chat import MessageDto
from app.adapter.store.models import Message

if TYPE_CHECKING:
    from app.adapter.store.sql_adapter import DataBaseAdapter


class MessageAdapter:
    async def save_message(
        self: 'DataBaseAdapter',
        msg: 'MessageDto',
    ) -> 'MessageDto':
        async with self._sc() as session:
            m_message = Message(
                sender_id=msg.sender_id,
                chat_id=msg.chat_id,
                text=msg.text,
            )
            session.add(m_message)
            await session.commit()
            return MessageDto.from_orm(m_message)
