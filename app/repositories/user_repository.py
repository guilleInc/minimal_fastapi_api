from typing import Protocol

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users import User, UserCreate, UserUpdate
from app.models.user_model import UserModel


class UserRepositoryError(Exception):
    """Raised when a user repository operation fails."""

    pass


class UserRepository(Protocol):
    async def add_user(self, payload: UserCreate) -> User: ...

    async def get_users(self) -> list[User]: ...

    async def get_user(self, user_id: int) -> User | None: ...

    async def update_user(self, user_id: int, payload: UserUpdate) -> User | None: ...

    async def delete_user(self, user_id: int) -> bool: ...


class SqlaUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_user(self, payload: UserCreate) -> User:
        try:
            stmt = insert(UserModel).values(**payload.model_dump()).returning(UserModel)
            user = await self.session.scalar(stmt)
            return User.model_validate(user)
        except Exception as exc:
            raise UserRepositoryError from exc

    async def get_users(self) -> list[User]:
        try:
            stmt = select(UserModel)
            users = await self.session.scalars(stmt)
            return [User.model_validate(user) for user in users]
        except Exception as exc:
            raise UserRepositoryError from exc

    async def get_user(self, user_id: int) -> User | None:
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            user = await self.session.scalar(stmt)
            return User.model_validate(user) if user else None
        except Exception as exc:
            raise UserRepositoryError from exc

    async def update_user(self, user_id: int, payload: UserUpdate) -> User | None:
        try:
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
        except Exception as exc:
            raise UserRepositoryError from exc

    async def delete_user(self, user_id: int) -> bool:
        try:
            stmt = delete(UserModel).where(UserModel.id == user_id).returning(UserModel.id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except Exception as exc:
            raise UserRepositoryError from exc
