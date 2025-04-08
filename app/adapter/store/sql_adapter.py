from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.settings import WS_DATA_BASE_DSN, WS_DATA_BASE_ECHO
from typing import TYPE_CHECKING
from app.adapter.store.user import UserAdapter
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


class DataBaseAdapter(UserAdapter):

    _engine: 'AsyncEngine' = None
    _sc: 'async_sessionmaker[AsyncSession]' = None

    def __init__(self):
        self._engine = create_async_engine(WS_DATA_BASE_DSN, echo=WS_DATA_BASE_ECHO, future=True)
        self._sc = async_sessionmaker(self._engine, expire_on_commit=False)

    def get_session(self) -> 'async_sessionmaker[AsyncSession]':
        return self._sc
