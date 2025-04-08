from app.adapter.store.models import User, UserJwt
from app.adapter.dto import UserDto, TokenDto
from app.adapter.hasher import generate_password_hash, check_password_hash
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select
from typing import TYPE_CHECKING
from sqlalchemy.orm import selectinload

if TYPE_CHECKING:
    from app.adapter.store.adapter import DataBaseAdapter
    from uuid import UUID


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
            await session.commit()
            return UserDto(
                user_id=user.id,
                username=username,
                email=user.email,
            )

    async def get_user_witch_check_password(
        self: 'DataBaseAdapter',
        username: 'str',
        password: 'str',
    ) -> 'UserDto|None':

        async with self._sc() as session:
            query = select(User).where(User.username == username)
            result = await session.execute(query)

            try:
                user = result.scalars().one()
            except NoResultFound:
                return None

            if check_password_hash(password, user.password_hash):
                return UserDto(
                    user_id=user.id,
                    username=user.username,
                    email=user.email,
                )
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
            query = select(User).where(User.id==user_id)
            result = await session.execute(query)
            try:
                user = result.scalars().one()
            except NoResultFound:
                return None
            return UserDto(
                user_id=user.id,
                username=user.username,
                email=user.email,
            )
