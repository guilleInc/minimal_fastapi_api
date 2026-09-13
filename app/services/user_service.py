from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users import User, UserIn, UserInDB
from app.repositories.user_repository import UserRepository
from app.security.password_hasher import PasswordHasher
from app.services.user_service_errors import UserServiceError
from app.utils import exception_boundary


class UserService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self.session = session
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    @exception_boundary(UserServiceError)
    async def add_user(self, payload: UserIn) -> User:
        existing_user = await self.user_repository.get_user_by_username(payload.username)
        if existing_user:
            raise UserServiceError("User already exists")

        user_in_db = UserInDB(
            username=payload.username,
            password_hash=self.password_hasher.hash(payload.password),
            is_active=True,
        )
        user = await self.user_repository.add_user(user_in_db)
        await self.session.commit()
        return user
