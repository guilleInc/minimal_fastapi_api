from pwdlib import PasswordHash

from app.domain.users import UserIn
from app.repositories.user_repository import UserRepository
from app.security.token_manager import Token, TokenError, TokenManager
from app.services.auth_service_errors import InvalidCredentialsError

password_hash = PasswordHash.recommended()


class AuthService:
    def __init__(
        self,
        token_manager: TokenManager,
        user_repository: UserRepository | None = None,
    ) -> None:
        self.token_manager = token_manager
        self.user_repository = user_repository

    async def authenticate_user(self, payload: UserIn) -> Token:
        if self.user_repository is None:
            raise InvalidCredentialsError()

        user = await self.user_repository.get_user_by_username(payload.username)

        if (
            not user
            or not user.is_active
            or not password_hash.verify(payload.password, user.password_hash)
        ):
            raise InvalidCredentialsError()

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
