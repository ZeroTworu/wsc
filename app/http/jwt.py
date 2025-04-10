import datetime
import uuid
from typing import TYPE_CHECKING

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.settings import (
    WS_ACCESS_TOKEN_EXPIRE_MINUTES, WS_ALGORITHM, WS_SECRET_KEY,
)

if TYPE_CHECKING:
    from app.adapter.dto import UserDto
    from app.adapter.store.adapter import DataBaseAdapter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


async def create_access_token(user: 'UserDto', adapter: 'DataBaseAdapter') -> 'str':
    payload = {
        'sub': str(user.user_id),
        'email': user.email,
        'username': user.username,
    }
    delta = datetime.timedelta(minutes=WS_ACCESS_TOKEN_EXPIRE_MINUTES) or datetime.timedelta(minutes=15)
    expire = datetime.datetime.now(datetime.UTC) + delta
    payload.update({'exp': expire})
    encoded_jwt = jwt.encode(payload, WS_SECRET_KEY, algorithm=WS_ALGORITHM)
    await adapter.create_jwt(user, encoded_jwt)
    return encoded_jwt


async def get_current_user(token: 'str', adapter: 'DataBaseAdapter',) -> 'UserDto':
    credentials_exception = HTTPException(status_code=401, detail='Could not validate credentials')
    try:
        payload = jwt.decode(token, WS_SECRET_KEY, algorithms=[WS_ALGORITHM])
    except JWTError:
        raise credentials_exception

    user_id = payload.get('sub')
    if user_id is None:
        raise credentials_exception

    result = await adapter.get_user_by_id(uuid.UUID(user_id))
    if not result:
        raise credentials_exception
    return result
