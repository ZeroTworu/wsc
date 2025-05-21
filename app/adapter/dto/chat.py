from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

from pydantic import (
    BaseModel, ConfigDict, Field, field_serializer, field_validator,
)

from app.adapter.dto.user import UserDto, UserResponseDto


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
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_dates(self, dt: datetime) -> int:
        return int(dt.timestamp())


class ChatHistoryMessageDto(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
    chat_id: UUID
    text: str
    sender: UserDto
    created_at: datetime
    updated_at: datetime
    message_id: UUID = Field(alias='id')
    readers: List[UserDto] = Field(default_factory=list)


class ChatHistoryMessageResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={datetime: lambda dt: int(dt.timestamp())},
    )

    chat_id: UUID
    text: str
    user: UserResponseDto
    created_at: datetime
    updated_at: datetime
    message_id: UUID = Field(alias='id')
    readers: List[UserResponseDto] = Field(default_factory=list)

    @field_validator('user', 'readers', mode='before')
    @classmethod
    def convert_users(cls, value):
        if isinstance(value, UserDto):
            return UserResponseDto.model_validate(value.model_dump())
        if isinstance(value, list):
            return [UserResponseDto.model_validate(u.model_dump()) for u in value]  # noqa: WPS111
        return value
