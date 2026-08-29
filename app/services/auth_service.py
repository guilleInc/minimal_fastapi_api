from app.security.token_manager import Token, TokenError, TokenManager
from app.services.auth_service_errors import InvalidCredentialsError


class AuthService:
    def __init__(self, token_manager: TokenManager) -> None:
        self.token_manager = token_manager

    def create_access_token(
        self,
        name: str,
        expires_delta: int | None = None,
    ) -> Token:
        if not name.strip():
            raise ValueError("Token name cannot be empty")

        access_token = self.token_manager.create_access_token(
            {"name": name},
            expires_delta=expires_delta,
        )
        return Token(access_token=access_token, token_type="bearer")

    def verify_access_token(self, token: str) -> str:
        try:
            payload = self.token_manager.decode_access_token(token)
        except TokenError as exc:
            raise InvalidCredentialsError() from exc

        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            raise InvalidCredentialsError()

        return name
