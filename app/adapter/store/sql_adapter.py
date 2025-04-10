from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)

from app.adapter.store.chat import ChatAdapter
from app.adapter.store.messages import MessageAdapter
from app.adapter.store.user import UserAdapter
from app.settings import WS_DATA_BASE_DSN, WS_DATA_BASE_ECHO

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

from app.logger import get_logger


class DataBaseAdapter(UserAdapter, ChatAdapter, MessageAdapter):

    _logger = get_logger('DataBaseAdapter')

    _engine: 'AsyncEngine' = None
    _sc: 'async_sessionmaker[AsyncSession]' = None

    def __init__(self):
        self._engine = create_async_engine(WS_DATA_BASE_DSN, echo=WS_DATA_BASE_ECHO, future=True)
        self._sc = async_sessionmaker(self._engine, expire_on_commit=False)

    def get_session(self) -> 'async_sessionmaker[AsyncSession]':
        return self._sc
