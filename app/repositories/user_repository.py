from typing import Protocol

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users import User, UserCreate, UserCredentials, UserUpdate
from app.models.user_model import UserModel
from app.utils import exception_boundary


class UserRepositoryError(Exception):
    """Raised when a user repository operation fails."""

    ...


class UserIntegrityError(UserRepositoryError):
    """Raised when a user violates a database integrity constraint."""

    ...


class UserRepository(Protocol):
    async def add_user(self, payload: UserCreate) -> User: ...

    async def get_user_credentials(self, username: str) -> UserCredentials | None: ...

    async def get_user_by_username(self, username: str) -> User | None: ...

    async def get_users(self) -> list[User]: ...

    async def get_user(self, user_id: int) -> User | None: ...

    async def update_user(self, user_id: int, payload: UserUpdate) -> User | None: ...

    async def delete_user(self, user_id: int) -> bool: ...


class SqlaUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @exception_boundary(UserRepositoryError)
    async def add_user(self, payload: UserCreate) -> User:
        stmt = insert(UserModel).values(**payload.model_dump()).returning(UserModel)
        try:
            user = await self.session.scalar(stmt)
        except IntegrityError as e:
            raise UserIntegrityError from e

        return User.model_validate(user)

    @exception_boundary(UserRepositoryError)
    async def get_user_credentials(self, username: str) -> UserCredentials | None:

        stmt = select(UserModel).where(UserModel.username == username)
        user = await self.session.scalar(stmt)
        return UserCredentials.model_validate(user) if user else None

    @exception_boundary(UserRepositoryError)
    async def get_user_by_username(self, username: str) -> User | None:

        stmt = select(UserModel).where(UserModel.username == username)
        user = await self.session.scalar(stmt)
        return User.model_validate(user) if user else None

    @exception_boundary(UserRepositoryError)
    async def get_user(self, user_id: int) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        user = await self.session.scalar(stmt)
        return User.model_validate(user) if user else None

    @exception_boundary(UserRepositoryError)
    async def get_users(self) -> list[User]:
        stmt = select(UserModel)
        users = await self.session.scalars(stmt)
        return [User.model_validate(user) for user in users]

    @exception_boundary(UserRepositoryError)
    async def update_user(self, user_id: int, payload: UserUpdate) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        user_orm = await self.session.scalar(stmt)
        if user_orm is None:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**update_data)
            .returning(UserModel)
        )
        updated_user = await self.session.scalar(stmt)
        return User.model_validate(updated_user)

    @exception_boundary(UserRepositoryError)
    async def delete_user(self, user_id: int) -> bool:
        stmt = delete(UserModel).where(UserModel.id == user_id).returning(UserModel.id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
