from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

from fastapi import WebSocket
from pydantic import BaseModel, ConfigDict, field_serializer

from app.adapter.dto.user import UserDto


class WebSocketEventType(Enum):
    MESSAGE = 'MESSAGE'
    USER_JOIN_CHAT = 'USER_JOIN_CHAT'
    USER_LEFT_CHAT = 'USER_LEFT_CHAT'
    PING = 'PING'
    PONG = 'PONG'
    UPDATE_READERS = 'UPDATE_READERS'


class WebSocketEvent(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda dt: int(dt.timestamp())},
    )

    type: WebSocketEventType
    ws: WebSocket
    user: UserDto
    readers: List[UserDto] = []

    chat_id: UUID | None = None
    message_id: UUID | None = None
    user_id: UUID | None = None
    message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def host_port(self) -> str:
        return f'{self.ws.client.host}:{self.ws.client.port}'  # noqa: WPS237

    @field_serializer('created_at', 'updated_at')
    def serialize_dates(self, dt: datetime) -> int | None:
        if dt is None:
            return None
        return int(dt.timestamp())
