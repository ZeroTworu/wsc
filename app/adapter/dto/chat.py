from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.adapter.dto.user import UserDto


class ChatType(Enum):
    PRIVATE = 'PRIVATE'
    GROUP = 'GROUP'


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


class MessageDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    message_id: UUID = Field(alias='id')
    sender_id: UUID
    chat_id: UUID
    message: str
    is_read: bool = False
