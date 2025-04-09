from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, WebSocketDisconnect

from app.http.jwt import get_current_user

if TYPE_CHECKING:
    from typing import Dict
    from uuid import UUID

    from fastapi import WebSocket

    from app.adapter.dto import UserDto

ws_rout = APIRouter(prefix='/ws')

active_connections: 'Dict[UUID, list[WebSocket]]' = {}


async def connect_user(user: 'UserDto', websocket: 'WebSocket'):
    await websocket.accept()
    active_connections.setdefault(user.user_id, []).append(websocket)


async def disconnect_user(user: 'UserDto', websocket: 'WebSocket'):
    active_connections[user.user_id].remove(websocket)


async def broadcast(user_id: 'UUID', message: 'str'):
    for conn in active_connections.get(user_id, []):
        await conn.send_text(message)


@ws_rout.websocket('/chat')
async def websocket_endpoint(ws: 'WebSocket', user: 'UserDto' = Depends(get_current_user)):
    await connect_user(user, ws)
    try:
        while True:
            msg = await ws.receive_text()
            await broadcast(user.id, f"{user.name}: {msg}")
    except WebSocketDisconnect:
        await disconnect_user(user, ws)
