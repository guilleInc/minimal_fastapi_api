from app.security.token_manager import Token, TokenError, TokenManager
from app.services.auth_service_errors import InvalidCredentialsError


class AuthService:
    def __init__(self, token_manager: TokenManager) -> None:
        self.token_manager = token_manager

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
