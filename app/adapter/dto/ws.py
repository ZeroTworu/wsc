from enum import Enum
from uuid import UUID

from fastapi import WebSocket
from pydantic import BaseModel, ConfigDict

from app.adapter.dto.user import UserDto


class WebSocketEventType(Enum):
    MESSAGE = 'MESSAGE'
    USER_JOIN_CHAT = 'USER_JOIN_CHAT'
    USER_LEFT_CHAT = 'USER_LEFT_CHAT'
    PING = 'PING'
    PONG = 'PONG'


class WebSocketEvent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: WebSocketEventType
    ws: WebSocket
    user: UserDto
    chat_id: UUID | None = None
    message: str | None = None

    @property
    def host_port(self) -> str:
        return f'{self.ws.client.host}:{self.ws.client.port}'  # noqa: WPS237
