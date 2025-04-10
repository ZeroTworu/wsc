from asyncio import gather
from fastapi import APIRouter, Depends, WebSocketDisconnect, WebSocket
from pydantic import ValidationError as PydanticValidationError
from starlette.websockets import WebSocketState
from app.http.api.auth import auth_ws
from app.adapter.dto import UserDto, WebSocketEvent, WebSocketEventType
from app.adapter import get_database_adapter, DataBaseAdapter
from app.logger import get_logger

from typing import Dict
from uuid import UUID

_logger = get_logger('Websocket')

ws_rout = APIRouter(prefix='/ws')

active_connections: 'Dict[UUID, list[WebSocket]]' = {}


async def connect_user(user: 'UserDto', websocket: 'WebSocket'):
    await websocket.accept()
    active_connections.setdefault(user.user_id, []).append(websocket)
    _logger.info(f'Added connection for %s,  %s:%d', user.user_id, websocket.client.host, websocket.client.port)


async def disconnect_user(user: 'UserDto', websocket: 'WebSocket'):
    active_connections[user.user_id].remove(websocket)
    _logger.info('Remove connection for %s,  %s:%d', user.user_id, websocket.client.host, websocket.client.port)
    if websocket.client_state == WebSocketState.CONNECTED:
        await websocket.close()


async def broadcast_to_user(user_id: 'UUID', message: 'str', chat_id: 'UUID|None' = None):
    msg = {'type': WebSocketEventType.MESSAGE.value, 'message': message, 'chat_id': str(chat_id)}
    await gather(*(conn.send_json(msg) for conn in active_connections.get(user_id, [])))

async def broadcast_to_chat(wse: WebSocketEvent, adapter: DataBaseAdapter):
    chat = await adapter.get_chat_by_id(wse.chat_id)
    if chat is None:
        _logger.warning(f'No chat for {wse.chat_id}')
        return
    for user in chat.participants:
        await broadcast_to_user(user.user_id, wse.message, chat.chat_id)

async def handle_ws_event(wse: WebSocketEvent, adapter: DataBaseAdapter):
    match wse.type:
        case WebSocketEventType.PING | WebSocketEventType.PONG: _logger.info(f'Received {wse.type} from {wse.host_port}: ')
        case WebSocketEventType.MESSAGE:
            await broadcast_to_chat(wse, adapter)
        case _: _logger.info(f'Not handled {wse.type}')


@ws_rout.websocket('/subscribe')
async def websocket_endpoint(ws: WebSocket, user: UserDto = Depends(auth_ws), adapter: DataBaseAdapter = Depends(get_database_adapter)):
    await connect_user(user, ws)
    try:
        async for msg in ws.iter_json():
            _logger.info(f'{user.user_id} {user.username}: {msg}')
            try:
                msg.update({'ws': ws})
                event = WebSocketEvent.model_validate(msg)
                await handle_ws_event(event, adapter)
            except PydanticValidationError as pve:
                _logger.error(f'Invalid WebSocket message: {pve}')
                # await disconnect_user(user, ws)
        await disconnect_user(user, ws)
    except WebSocketDisconnect:
        await disconnect_user(user, ws)
