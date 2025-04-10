from enum import Enum
from typing import List
from uuid import UUID
from fastapi import WebSocket
from pydantic import BaseModel, ConfigDict, Field


class ChatType(Enum):
    PRIVATE = 'PRIVATE'
    GROUP = 'GROUP'

class WebSocketEventType(Enum):
  PING = 'PING'
  PONG= 'PONG'
  MESSAGE = 'MESSAGE'
  USER_JOIN_CHAT = 'USER_JOIN_CHAT'
  USER_LEFT_CHAT = 'USER_LEFT_CHAT'

class WebSocketEvent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: WebSocketEventType
    ws: WebSocket
    chat_id: UUID | None = None
    message: str | None = None

    @property
    def host_port(self) -> str:
        return f'{self.ws.client.host}:{self.ws.client.port}'

class UserDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID = Field(alias='id', serialization_alias='user_id')
    email: str
    username: str


class UserCreateDto(BaseModel):
    email: str
    username: str
    password: str


class TokenDto(BaseModel):
    access_token: str
    user_id: UUID
    newer_expired: bool = False


class ChatCreateDto(BaseModel):
    chat_name: str
    chat_type: ChatType
    participants: List[UUID]


class ChatDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    chat_id: UUID = Field(..., alias='id')
    chat_name: str
    chat_type: ChatType
    owner_id: UUID
    participants: List[UserDto]
