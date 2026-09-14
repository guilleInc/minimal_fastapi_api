from app.domain.users import UserIn
from app.repositories.user_repository import UserRepository
from app.security.password_hasher import PasswordHasher
from app.security.token_manager import Token, TokenError, TokenManager
from app.services.auth_service_errors import InvalidCredentialsError


class AuthService:
    def __init__(
        self,
        token_manager: TokenManager,
        password_hasher: PasswordHasher,
        user_repository: UserRepository,
    ) -> None:
        self.token_manager = token_manager
        self.password_hasher = password_hasher
        self.user_repository = user_repository

    async def authenticate_user(self, payload: UserIn) -> Token:
        user = await self.user_repository.get_user_by_username(payload.username)
        if not user:
            raise InvalidCredentialsError("User not found")

        if not user.is_active:
            raise InvalidCredentialsError("User is inactive")

        if not self.password_hasher.verify(payload.password, user.password_hash):
            raise InvalidCredentialsError("Invalid password")

        return self.create_access_token(user.username)

    def create_access_token(
        self,
        user: str,
        expires_delta: int | None = None,
    ) -> Token:
        if not user.strip():
            raise ValueError("User name cannot be empty")

        access_token = self.token_manager.create_access_token(
            {"user": user},
            expires_delta=expires_delta,
        )
        return Token(access_token=access_token, token_type="bearer")

    def verify_access_token(self, token: str) -> str:
        try:
            payload = self.token_manager.decode_access_token(token)
        except TokenError as exc:
            raise InvalidCredentialsError() from exc

        user = payload.get("user")
        if not isinstance(user, str) or not user.strip():
            raise InvalidCredentialsError()

        return user
