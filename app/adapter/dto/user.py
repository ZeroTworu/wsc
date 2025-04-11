from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
