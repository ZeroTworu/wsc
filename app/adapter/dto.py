from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatType(Enum):
    PRIVATE = 'PRIVATE'
    GROUP = 'GROUP'


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
