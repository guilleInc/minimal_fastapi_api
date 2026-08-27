from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users import User, UserCreate, UserRegister
from app.repositories.user_repository import UserIntegrityError, UserRepository
from app.security import PasswordHasher
from app.security.token_manager import Token, TokenManager
from app.services.auth_service_errors import (
    AuthServiceError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.utils import exception_boundary


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_manager: TokenManager,
    ) -> None:
        self.session = session
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_manager = token_manager

    @exception_boundary(AuthServiceError)
    async def register_user(self, payload: UserRegister) -> User:
        user_create = UserCreate(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            disabled=payload.disabled,
            hashed_password=self.password_hasher.hash(payload.password),
        )

        try:
            user = await self.user_repository.add_user(user_create)
        except UserIntegrityError as exc:
            raise UserAlreadyExistsError from exc

        await self.session.commit()
        return user

    @exception_boundary(AuthServiceError)
    async def authenticate_user(self, username: str, password: str) -> Token | None:
        user_credentials = await self.user_repository.get_user_credentials(username)
        if user_credentials is None:
            raise InvalidCredentialsError()
        if not self.password_hasher.verify(password, user_credentials.hashed_password):
            raise InvalidCredentialsError()
        token = self.token_manager.create_access_token({"sub": user_credentials.id})
        return Token(access_token=token, token_type="bearer")

    @exception_boundary(AuthServiceError)
    async def get_active_user(self, token: str) -> User:
        payload = self.token_manager.decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidCredentialsError()
        user = await self.user_repository.get_user(user_id)
        if user is None or user.disabled:
            raise InvalidCredentialsError()
        return user
