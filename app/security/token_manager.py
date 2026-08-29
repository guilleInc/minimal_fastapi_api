import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pydantic import BaseModel


class TokenError(Exception):
    """Raised when a token cannot be decoded or validated."""


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenManager:
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)

        to_encode["exp"] = expire
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_access_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"require": ["exp", "name"]},
            )
        except jwt.InvalidTokenError as exc:
            raise TokenError from exc


def get_token_manager() -> TokenManager:
    secret_key = os.environ.get("JWT_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required")

    algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
    return TokenManager(secret_key=secret_key, algorithm=algorithm)
