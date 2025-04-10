from typing import List

from fastapi import APIRouter, Depends

from app.adapter import get_database_adapter
from app.adapter.dto.user import UserDto
from app.adapter.store.sql_adapter import DataBaseAdapter
from app.http.api.auth import auth_http

users_rout = APIRouter(prefix='/api/users', tags=['users'])


@users_rout.get('/list/all', response_model=List[UserDto])
async def users_all(
        user: UserDto = Depends(auth_http),
        adapter: DataBaseAdapter = Depends(get_database_adapter),
) -> List[UserDto]:
    return await adapter.list_users(user.user_id)
