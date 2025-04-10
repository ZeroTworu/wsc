from typing import TYPE_CHECKING, List

from fastapi import APIRouter, Depends

from app.adapter import get_database_adapter
from app.adapter.dto.chat import ChatCreateDto, ChatDto, UserDto
from app.http.api.auth import auth_http

if TYPE_CHECKING:
    from app.adapter.store.sql_adapter import DataBaseAdapter

chat_rout = APIRouter(prefix='/api/chat', tags=['chat'])


@chat_rout.post('/create', response_model=ChatDto)
async def create_chat(
    data: ChatCreateDto,
    adapter: 'DataBaseAdapter' = Depends(get_database_adapter),
    user: 'UserDto' = Depends(auth_http),
) -> 'ChatDto':
    return await adapter.create_chat(owner_id=user.user_id, chat=data)


@chat_rout.get('/list/my', response_model=List[ChatDto])
async def my_chats(
    adapter: 'DataBaseAdapter' = Depends(get_database_adapter),
    user: 'UserDto' = Depends(auth_http),
) -> 'List[ChatDto]':
    return await adapter.get_my_chats(user_id=user.user_id)


@chat_rout.get('/list/all', response_model=List[ChatDto])
async def all_chats(
    adapter: 'DataBaseAdapter' = Depends(get_database_adapter),
    _: 'UserDto' = Depends(auth_http),  # В реальности не нужно, просто что бы сработал механизм аутентификации
) -> 'List[ChatDto]':
    return await adapter.get_all_chats()
