from unittest.mock import MagicMock

import pytest

from app.security.token_manager import Token, TokenError
from app.services.auth_service import AuthService
from app.services.auth_service_errors import InvalidCredentialsError


class TestCreateAccessToken:
    def test_creates_token_for_user(
        self, auth_service: AuthService, mock_token_manager: MagicMock
    ) -> None:
        # Arrange
        mock_token_manager.create_access_token.return_value = "access-token"

        # Act
        result = auth_service.create_access_token(user="alice", expires_delta=15)

        # Assert
        assert result == Token(access_token="access-token", token_type="bearer")
        mock_token_manager.create_access_token.assert_called_once_with(
            {"user": "alice"},
            expires_delta=15,
        )

    def test_rejects_empty_user(
        self, auth_service: AuthService, mock_token_manager: MagicMock
    ) -> None:
        # Arrange

        # Act and Assert
        with pytest.raises(ValueError, match="User name cannot be empty"):
            auth_service.create_access_token(user=" ")

        mock_token_manager.create_access_token.assert_not_called()


class TestVerifyAccessToken:
    def test_returns_user_from_valid_token(
        self, auth_service: AuthService, mock_token_manager: MagicMock
    ) -> None:
        # Arrange
        mock_token_manager.decode_access_token.return_value = {"user": "alice"}

        # Act
        result = auth_service.verify_access_token("access-token")

        # Assert
        assert result == "alice"
        mock_token_manager.decode_access_token.assert_called_once_with("access-token")

    def test_rejects_token_without_user(
        self, auth_service: AuthService, mock_token_manager: MagicMock
    ) -> None:
        # Arrange
        mock_token_manager.decode_access_token.return_value = {}

        # Act and Assert
        with pytest.raises(InvalidCredentialsError):
            auth_service.verify_access_token("access-token")

    def test_rejects_invalid_token(
        self, auth_service: AuthService, mock_token_manager: MagicMock
    ) -> None:
        # Arrange
        mock_token_manager.decode_access_token.side_effect = TokenError

        # Act and Assert
        with pytest.raises(InvalidCredentialsError):
            auth_service.verify_access_token("invalid-token")
