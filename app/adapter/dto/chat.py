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


class ChatDto(ChatCreateDto):
    model_config = ConfigDict(from_attributes=True)
    chat_id: UUID = Field(..., alias='id')
    owner_id: UUID
    participants: List[UserDto]


class ChatMessageCreateDto(BaseModel):
    sender_id: UUID
    chat_id: UUID
    text: str


class ChatMessageDto(ChatMessageCreateDto):
    model_config = ConfigDict(from_attributes=True)
    message_id: UUID = Field(alias='id')
    readers: List[UserDto] = Field(default_factory=list)
