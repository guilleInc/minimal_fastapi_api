from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users import User, UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from app.services.user_service_errors import UserNotFoundError, UserServiceError
from app.utils import exception_boundary


class UserService:
    def __init__(self, session: AsyncSession, user_repository: UserRepository) -> None:
        self.session = session
        self.user_repository = user_repository

    @exception_boundary(UserServiceError)
    async def add_user(self, payload: UserCreate) -> User:
        user = await self.user_repository.add_user(payload)
        await self.session.commit()
        return user

    @exception_boundary(UserServiceError)
    async def get_users(self) -> list[User]:
        return await self.user_repository.get_users()

    @exception_boundary(UserServiceError)
    async def get_user(self, user_id: int) -> User:
        user = await self.user_repository.get_user(user_id)
        if user is None:
            raise UserNotFoundError()
        return user

    @exception_boundary(UserServiceError)
    async def update_user(self, user_id: int, payload: UserUpdate) -> User:
        user = await self.user_repository.update_user(user_id, payload)
        if user is None:
            raise UserNotFoundError()
        await self.session.commit()
        return user

    @exception_boundary(UserServiceError)
    async def delete_user(self, user_id: int) -> None:
        if not await self.user_repository.delete_user(user_id):
            raise UserNotFoundError()
        await self.session.commit()
