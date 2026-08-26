import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users import User, UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository, UserRepositoryError
from app.services.user_service_errors import UserNotFoundError, UserServiceError

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession, repository: UserRepository) -> None:
        self.session = session
        self.repository = repository

    async def add_user(self, payload: UserCreate) -> User:
        try:
            user = await self.repository.add_user(payload)
            await self.session.commit()
            return user
        except UserRepositoryError as exc:
            logger.exception("Failed to add user")
            raise UserServiceError() from exc

    async def get_users(self) -> list[User]:
        try:
            return await self.repository.get_users()
        except UserRepositoryError as exc:
            logger.exception("Failed to get users")
            raise UserServiceError() from exc

    async def get_user(self, user_id: int) -> User:
        try:
            user = await self.repository.get_user(user_id)
            if user is None:
                raise UserNotFoundError()
            return user
        except UserRepositoryError as exc:
            logger.exception("Failed to get user %d", user_id)
            raise UserServiceError() from exc

    async def update_user(self, user_id: int, payload: UserUpdate) -> User:
        try:
            user = await self.repository.update_user(user_id, payload)
            if user is None:
                raise UserNotFoundError()
            await self.session.commit()
            return user
        except UserRepositoryError as exc:
            logger.exception("Failed to update user %d", user_id)
            raise UserServiceError() from exc

    async def delete_user(self, user_id: int) -> None:
        try:
            if not await self.repository.delete_user(user_id):
                raise UserNotFoundError()
            await self.session.commit()
        except UserRepositoryError as exc:
            logger.exception("Failed to delete user %d", user_id)
            raise UserServiceError() from exc
