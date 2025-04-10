from asyncio import gather
from fastapi import APIRouter, Depends, WebSocketDisconnect, WebSocket
from starlette.websockets import WebSocketState

from app.http.api.auth import auth_ws
from app.adapter.dto import UserDto
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
    await websocket.close()
    _logger.info(f'Close connection for %s,  %s:%d', user.user_id, websocket.client.host, websocket.client.port)


async def broadcast(user_id: 'UUID', message: 'str'):
    await gather(*(conn.send_text(message) for conn in active_connections.get(user_id, [])))

@ws_rout.websocket('/subscribe')
async def websocket_endpoint(ws: WebSocket, user: UserDto = Depends(auth_ws)):
    await connect_user(user, ws)
    try:
        while ws.client_state == WebSocketState.CONNECTED:
            msg = await ws.receive_json()
            _logger.info(f'{user.user_id} {user.username}: {msg}')
    except WebSocketDisconnect:
        await disconnect_user(user, ws)
