from uuid import UUID

from pydantic import BaseModel

class UserDto(BaseModel):
    user_id: UUID
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