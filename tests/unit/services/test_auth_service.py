from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.users import User, UserCreate, UserCredentials, UserRegister
from app.repositories.user_repository import UserIntegrityError, UserRepositoryError
from app.security.token_manager import Token
from app.services.auth_service import AuthService
from app.services.auth_service_errors import (
    AuthServiceError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)


class TestRegisterUser:
    """Tests for AuthService.register_user()."""

    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        auth_service: AuthService,
        user_mock_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test successfully registering a user."""
        # Arrange
        payload = UserRegister(
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=False,
            password="secret",
        )
        expected_create = UserCreate(
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=False,
            hashed_password="hashed-secret",
        )
        expected_user = User(
            id=1,
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=False,
        )
        mock_password_hasher.hash.return_value = "hashed-secret"
        user_mock_repository.add_user.return_value = expected_user

        # Act
        result = await auth_service.register_user(payload)

        # Assert
        assert result == expected_user
        mock_password_hasher.hash.assert_called_once_with("secret")
        user_mock_repository.add_user.assert_called_once_with(expected_create)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_duplicate_raises_user_already_exists(
        self,
        auth_service: AuthService,
        user_mock_repository: AsyncMock,
        mock_password_hasher: MagicMock,
    ) -> None:
        """Test duplicate registration raises UserAlreadyExistsError."""
        # Arrange
        payload = UserRegister(
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=False,
            password="secret",
        )
        mock_password_hasher.hash.return_value = "hashed-secret"
        user_mock_repository.add_user.side_effect = UserIntegrityError()

        # Act and Assert
        with pytest.raises(UserAlreadyExistsError):
            await auth_service.register_user(payload)

    @pytest.mark.asyncio
    async def test_register_user_repository_error_raises_auth_service_error(
        self,
        auth_service: AuthService,
        user_mock_repository: AsyncMock,
        mock_password_hasher: MagicMock,
    ) -> None:
        """Test repository failures are exposed as AuthServiceError."""
        # Arrange
        payload = UserRegister(
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=False,
            password="secret",
        )
        mock_password_hasher.hash.return_value = "hashed-secret"
        user_mock_repository.add_user.side_effect = UserRepositoryError("DB error")

        # Act and Assert
        with pytest.raises(AuthServiceError):
            await auth_service.register_user(payload)


class TestAuthenticateUser:
    """Tests for AuthService.authenticate_user()."""

    @pytest.mark.asyncio
    async def test_authenticate_user_success(
        self,
        auth_service: AuthService,
        user_mock_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_token_manager: MagicMock,
    ) -> None:
        """Test successfully authenticating a user."""
        # Arrange
        credentials = UserCredentials(
            id=1,
            username="alice",
            email="alice@example.com",
            hashed_password="hashed-secret",
        )
        user_mock_repository.get_user_credentials.return_value = credentials
        mock_password_hasher.verify.return_value = True
        mock_token_manager.create_access_token.return_value = "access-token"

        # Act
        result = await auth_service.authenticate_user("alice", "secret")

        # Assert
        assert result == Token(access_token="access-token", token_type="bearer")
        user_mock_repository.get_user_credentials.assert_called_once_with("alice")
        mock_password_hasher.verify.assert_called_once_with("secret", "hashed-secret")
        mock_token_manager.create_access_token.assert_called_once_with({"sub": 1})

    @pytest.mark.asyncio
    async def test_authenticate_user_missing_credentials(
        self, auth_service: AuthService, user_mock_repository: AsyncMock
    ) -> None:
        """Test authentication fails when the username does not exist."""
        # Arrange
        user_mock_repository.get_user_credentials.return_value = None

        # Act and Assert
        with pytest.raises(InvalidCredentialsError):
            await auth_service.authenticate_user("missing", "secret")

        user_mock_repository.get_user_credentials.assert_called_once_with("missing")

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(
        self,
        auth_service: AuthService,
        user_mock_repository: AsyncMock,
        mock_password_hasher: MagicMock,
    ) -> None:
        """Test authentication fails when the password is invalid."""
        # Arrange
        credentials = UserCredentials(
            id=1,
            username="alice",
            email="alice@example.com",
            hashed_password="hashed-secret",
        )
        user_mock_repository.get_user_credentials.return_value = credentials
        mock_password_hasher.verify.return_value = False

        # Act and Assert
        with pytest.raises(InvalidCredentialsError):
            await auth_service.authenticate_user("alice", "wrong")

        mock_password_hasher.verify.assert_called_once_with("wrong", "hashed-secret")


class TestGetActiveUser:
    """Tests for AuthService.get_active_user()."""

    @pytest.mark.asyncio
    async def test_get_active_user_success(
        self,
        auth_service: AuthService,
        user_mock_repository: AsyncMock,
        mock_token_manager: MagicMock,
    ) -> None:
        """Test successfully retrieving the active user from a token."""
        # Arrange
        user = User(
            id=1,
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=False,
        )
        mock_token_manager.decode_access_token.return_value = {"sub": 1}
        user_mock_repository.get_user.return_value = user

        # Act
        result = await auth_service.get_active_user("access-token")

        # Assert
        assert result == user
        mock_token_manager.decode_access_token.assert_called_once_with("access-token")
        user_mock_repository.get_user.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_active_user_missing_subject(
        self, auth_service: AuthService, mock_token_manager: MagicMock
    ) -> None:
        """Test active user lookup fails when a token has no subject."""
        # Arrange
        mock_token_manager.decode_access_token.return_value = {}

        # Act and Assert
        with pytest.raises(InvalidCredentialsError):
            await auth_service.get_active_user("invalid-token")

    @pytest.mark.asyncio
    async def test_get_active_user_not_found(
        self,
        auth_service: AuthService,
        user_mock_repository: AsyncMock,
        mock_token_manager: MagicMock,
    ) -> None:
        """Test active user lookup fails when the user does not exist."""
        # Arrange
        mock_token_manager.decode_access_token.return_value = {"sub": 999}
        user_mock_repository.get_user.return_value = None

        # Act and Assert
        with pytest.raises(InvalidCredentialsError):
            await auth_service.get_active_user("access-token")

        user_mock_repository.get_user.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_get_active_user_disabled(
        self,
        auth_service: AuthService,
        user_mock_repository: AsyncMock,
        mock_token_manager: MagicMock,
    ) -> None:
        """Test active user lookup fails for a disabled user."""
        # Arrange
        disabled_user = User(
            id=1,
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=True,
        )
        mock_token_manager.decode_access_token.return_value = {"sub": 1}
        user_mock_repository.get_user.return_value = disabled_user

        # Act and Assert
        with pytest.raises(InvalidCredentialsError):
            await auth_service.get_active_user("access-token")
