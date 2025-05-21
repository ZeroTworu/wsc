from asyncio import gather
from typing import Dict
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket
from pydantic import ValidationError as PydanticValidationError
from starlette.websockets import WebSocketState

from app.adapter import DataBaseAdapter, get_database_adapter
from app.adapter.dto.chat import ChatMessageCreateDto
from app.adapter.dto.user import UserDto
from app.adapter.dto.ws import WebSocketEvent, WebSocketEventType
from app.http.api.auth import auth_ws
from app.logger import get_logger

_logger = get_logger('Websocket')

ws_rout = APIRouter(prefix='/ws')

active_connections: 'Dict[UUID, list[WebSocket]]' = {}


async def connect_user(user: 'UserDto', websocket: 'WebSocket'):
    await websocket.accept()
    active_connections.setdefault(user.user_id, []).append(websocket)
    _logger.info('Added connection for %s,  %s:%d', user.user_id, websocket.client.host, websocket.client.port)


async def disconnect_user(user: 'UserDto', websocket: 'WebSocket'):
    active_connections[user.user_id].remove(websocket)
    _logger.info('Remove connection for %s,  %s:%d', user.user_id, websocket.client.host, websocket.client.port)
    if websocket.client_state == WebSocketState.CONNECTED:
        await websocket.close()


async def broadcast_to_user(wse: WebSocketEvent, user_id: UUID):
    exclude = {
        'ws': True,
        'user': {'email'},
    }
    payload = wse.model_dump_json(exclude=exclude)
    coroutines = [conn.send_text(payload) for conn in active_connections.get(user_id, [])]
    await gather(*coroutines)


async def broadcast_new_message(wse: WebSocketEvent, adapter: DataBaseAdapter):
    _logger.info('Broadcast new message for %s', wse)
    chat = await adapter.get_chat_by_id_and_user_id(wse.chat_id, wse.user.user_id)
    if chat is None:
        _logger.warning(f'No chat for {wse.chat_id}')
        return
    saved_message = await adapter.save_message(
        ChatMessageCreateDto(
            sender_id=wse.user.user_id,
            chat_id=wse.chat_id,
            text=wse.message,
        ),
    )
    wse.message_id = saved_message.message_id
    wse.user_id = saved_message.sender_id
    wse.created_at = saved_message.created_at
    wse.updated_at = saved_message.updated_at

    coroutines = [broadcast_to_user(wse, user.user_id) for user in chat.participants]
    await gather(*coroutines)


async def broadcast_update_readers(wse: WebSocketEvent, adapter: DataBaseAdapter):
    _logger.info('Broadcast update readers for %s', wse)
    chat = await adapter.get_chat_by_id_and_user_id(wse.chat_id, wse.user.user_id)

    if chat is None:
        _logger.warning(f'No chat for {wse.chat_id}')
        return

    msg = await adapter.add_reader(wse.chat_id, wse.message_id, wse.user.user_id)
    wse.readers = msg.readers
    coroutines = [broadcast_to_user(wse, user.user_id) for user in chat.participants]
    await gather(*coroutines)


async def handle_ws_event(wse: WebSocketEvent, adapter: DataBaseAdapter):
    match wse.type:
        case WebSocketEventType.PING | WebSocketEventType.PONG:
            _logger.info(f'Received {wse.type} from {wse.host_port}: ')
        case WebSocketEventType.MESSAGE:
            await broadcast_new_message(wse, adapter)
        case WebSocketEventType.UPDATE_READERS:
            await broadcast_update_readers(wse, adapter)
        case _: _logger.info(f'Not handled {wse.type}')


@ws_rout.websocket('/subscribe')
async def websocket_endpoint(
        ws: WebSocket,
        user: UserDto = Depends(auth_ws),
        adapter: DataBaseAdapter = Depends(get_database_adapter),
):
    await connect_user(user, ws)
    async for msg in ws.iter_json():
        _logger.info(f'{user.user_id} {user.username}: {msg}')
        msg.update({'ws': ws, 'user': user})
        event = None
        try:
            event = WebSocketEvent.model_validate(msg)
        except PydanticValidationError as pve:
            _logger.error(f'Invalid WebSocket message: {pve}')
            await disconnect_user(user, ws)
        if event is not None:
            await handle_ws_event(event, adapter)
    await disconnect_user(user, ws)
