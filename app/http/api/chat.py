from typing import TYPE_CHECKING, List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.adapter import get_database_adapter
from app.adapter.dto.chat import (
    ChatCreateDto, ChatDto, ChatHistoryMessageResponse, UserDto,
)
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


@chat_rout.get('/history/{chat_id}', response_model=List[ChatHistoryMessageResponse])
async def chat_history(
    chat_id: 'UUID',
    offset: int = 0,
    limit: int = 5,
    adapter: 'DataBaseAdapter' = Depends(get_database_adapter),
    current_user: 'UserDto' = Depends(auth_http),
) -> List[ChatHistoryMessageResponse]:
    messages = await adapter.get_messages_by_chat_and_user_id(
        chat_id,
        current_user.user_id,
        offset,
        limit
    )

    return [
        ChatHistoryMessageResponse.model_validate({
            **msg.model_dump(),
            'user': msg.sender,
            'readers': msg.readers
        })
        for msg in messages
    ]


@chat_rout.delete('/leave/{chat_id}')
async def leave_chat(
    chat_id: 'UUID',
    adapter: 'DataBaseAdapter' = Depends(get_database_adapter),
    current_user: 'UserDto' = Depends(auth_http),
) -> 'bool':
    return await adapter.leave_chat(chat_id, current_user.user_id)
