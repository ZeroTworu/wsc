from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import selectinload
from starlette import status

from app.adapter.dto import TokenDto, UserDto
from app.adapter.hasher import check_password_hash, generate_password_hash
from app.adapter.store.models import User, UserJwt

if TYPE_CHECKING:
    from typing import List
    from uuid import UUID

    from app.adapter.store.sql_adapter import DataBaseAdapter


class UserAdapter:

    async def create_user(
        self: 'DataBaseAdapter',
        username: 'str',
        password: 'str',
        email: 'str' = None,
    ) -> 'UserDto':

        async with self._sc() as session:
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
            )
            session.add(user)
            try:
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail='Email & username already exists',
                ) from exc
            return UserDto(
                id=user.id,
                username=username,
                email=user.email,
            )

    async def get_user_witch_check_password(
        self: 'DataBaseAdapter',
        username: 'str',
        password: 'str',
    ) -> 'UserDto|None':
        self._logger.info('get_user_witch_check_password called with username=%s', username)
        async with self._sc() as session:
            query = select(User).where(User.username == username)
            result = await session.execute(query)

            try:
                user = result.scalars().one()
            except NoResultFound:
                self._logger.info('get_user_witch_check_password no user with username=%s', username)
                return None

            if check_password_hash(password, user.password_hash):
                return UserDto(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                )
            self._logger.info('get_user_witch_check_password incorrect password for username=%s', username)
            return None

    async def create_jwt(self: 'DataBaseAdapter', user: 'UserDto', token: 'str') -> 'TokenDto|None':

        async with self._sc() as session:
            token = UserJwt(
                token=token,
                owner_id=user.user_id,
            )
            session.add(token)
            await session.commit()
            return TokenDto(
                access_token=token.token,
                user_id=user.user_id,
            )

    async def get_jwt(self: 'DataBaseAdapter', token: 'str') -> 'UserJwt|None':

        async with self._sc() as session:
            query = select(UserJwt).where(UserJwt.token == token)
            result = await session.execute(query.options(selectinload(UserJwt.owner)))
            try:
                jwt = result.scalars().one()
            except NoResultFound:
                return None

            user = User(
                id=jwt.owner.id,
                username=jwt.owner.username,
            )
            return UserJwt(
                token=jwt.token,
                owner_id=user.id,
            )

    async def get_user_by_id(self: 'DataBaseAdapter', user_id: 'UUID') -> 'UserDto|None':
        async with self._sc() as session:
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            try:
                user = result.scalars().one()
            except NoResultFound:
                return None
            return UserDto(
                id=user.id,
                username=user.username,
                email=user.email,
            )

    async def list_users(self: 'DataBaseAdapter', exclude_user_id: 'UUID') -> 'List[UserDto]':
        async with self._sc() as session:
            result = await session.execute(
                select(User).where(User.id != exclude_user_id)
            )
            users = result.scalars().all()
            return [UserDto.model_validate(user) for user in users]
