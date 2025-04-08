from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.adapter.dto import UserDto, TokenDto, UserCreateDto
from app.adapter import get_database_adapter
from app.http.jwt import get_current_user, create_access_token
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.adapter.store.sql_adapter import DataBaseAdapter

auth_rout = APIRouter(prefix='/auth')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


async def auth(token: str = Depends(oauth2_scheme), adapter: str = Depends(get_database_adapter)) -> 'UserDto':
    return await get_current_user(token, adapter)


@auth_rout.get('/me')
async def user_me(user: 'UserDto' = Depends(auth)) -> UserDto:
    return user


@auth_rout.post('/login')
async def login(form_data: 'OAuth2PasswordRequestForm' = Depends(), adapter: 'DataBaseAdapter' = Depends(get_database_adapter)) -> dict[str, str]:
    user = await adapter.get_user_witch_check_password(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Wrong credentials')

    access_token = await create_access_token(user, adapter)
    return {'access_token': access_token, 'token_type': 'bearer'}


@auth_rout.post("/register", response_model=TokenDto)
async def register(user: 'UserCreateDto', adapter: 'DataBaseAdapter' = Depends(get_database_adapter)) -> TokenDto:
    user = await adapter.create_user(user.username, user.password, user.email)


    token = await create_access_token(user, adapter)
    return TokenDto(
        access_token=token,
        user_id=user.user_id,
        newer_expired=False,
    )
