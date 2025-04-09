from typing import TYPE_CHECKING, List

from fastapi import APIRouter, Depends

from app.adapter import get_database_adapter
from app.adapter.dto import UserDto
from app.http.api.auth import auth

if TYPE_CHECKING:
    from app.adapter.store.sql_adapter import DataBaseAdapter

users_rout = APIRouter(prefix='/api/users', tags=['users'])


@users_rout.get('/list')
async def user_me(
        user: 'UserDto' = Depends(auth),
        adapter: 'DataBaseAdapter' = Depends(get_database_adapter),
) -> 'List[UserDto]':
    return await adapter.list_users(user.user_id)
