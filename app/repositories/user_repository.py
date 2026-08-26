from typing import Protocol

from app.domain.users import User, UserCreate, UserUpdate


class UserRepositoryError(Exception):
    """Raised when a user repository operation fails."""

    pass


class UserRepository(Protocol):
    async def add_user(self, payload: UserCreate) -> User: ...

    async def get_users(self) -> list[User]: ...

    async def get_user(self, user_id: int) -> User | None: ...

    async def update_user(self, user_id: int, payload: UserUpdate) -> User | None: ...

    async def delete_user(self, user_id: int) -> bool: ...
