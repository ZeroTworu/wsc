from asyncio import gather
from typing import Dict
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket
from pydantic import ValidationError as PydanticValidationError
from starlette.websockets import WebSocketState

from app.adapter import DataBaseAdapter, get_database_adapter
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
        'user': {'user_id', 'email'},
    }
    payload = wse.model_dump_json(exclude=exclude)
    coroutines = [conn.send_text(payload) for conn in active_connections.get(user_id, [])]
    await gather(*coroutines)


async def broadcast_to_chat(wse: WebSocketEvent, adapter: DataBaseAdapter):
    chat = await adapter.get_chat_by_id(wse.chat_id)
    if chat is None:
        _logger.warning(f'No chat for {wse.chat_id}')
        return
    coroutines = [broadcast_to_user(wse, user.user_id) for user in chat.participants]
    await gather(*coroutines)


async def handle_ws_event(wse: WebSocketEvent, adapter: DataBaseAdapter):
    match wse.type:
        case WebSocketEventType.PING | WebSocketEventType.PONG:
            _logger.info(f'Received {wse.type} from {wse.host_port}: ')
        case WebSocketEventType.MESSAGE:
            await broadcast_to_chat(wse, adapter)
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
