from typing import Protocol

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users import User, UserCreateDB
from app.models.user_model import UserModel
from app.utils import exception_boundary


class UserRepositoryError(Exception):
    """Raised when a user repository operation fails."""

    ...


class UserRepository(Protocol):
    async def add_user(self, payload: UserCreateDB) -> User: ...

    async def get_user_by_username(self, username: str) -> User | None: ...

    async def delete_user(self, user_id: int) -> bool: ...

    async def deactivate_user(self, user_id: int) -> User | None: ...

    async def activate_user(self, user_id: int) -> User | None: ...


class SqlaUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @exception_boundary(UserRepositoryError)
    async def add_user(self, payload: UserCreateDB) -> User:
        stmt = insert(UserModel).values(**payload.model_dump()).returning(UserModel)
        user = await self.session.scalar(stmt)
        return User.model_validate(user)

    @exception_boundary(UserRepositoryError)
    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        user = await self.session.scalar(stmt)
        return User.model_validate(user) if user else None

    @exception_boundary(UserRepositoryError)
    async def delete_user(self, user_id: int) -> bool:
        stmt = delete(UserModel).where(UserModel.id == user_id).returning(UserModel.id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @exception_boundary(UserRepositoryError)
    async def deactivate_user(self, user_id: int) -> User | None:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=False)
            .returning(UserModel)
        )
        user = await self.session.scalar(stmt)
        return User.model_validate(user) if user else None

    @exception_boundary(UserRepositoryError)
    async def activate_user(self, user_id: int) -> User | None:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=True)
            .returning(UserModel)
        )
        user = await self.session.scalar(stmt)
        return User.model_validate(user) if user else None
