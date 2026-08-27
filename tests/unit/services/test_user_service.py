from unittest.mock import AsyncMock

import pytest

from app.domain.users import User, UserCreate, UserUpdate
from app.repositories.user_repository import UserRepositoryError
from app.services.user_service import UserService
from app.services.user_service_errors import UserNotFoundError, UserServiceError


class TestAddUser:
    """Tests for UserService.add_user()."""

    @pytest.mark.asyncio
    async def test_add_user_success(
        self,
        user_service: UserService,
        user_mock_repository: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test successfully adding a user."""
        # Arrange
        user_create = UserCreate(
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=False,
            hashed_password="hashed-password",
        )
        expected_user = User(
            id=1,
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=False,
        )
        user_mock_repository.add_user.return_value = expected_user

        # Act
        result = await user_service.add_user(user_create)

        # Assert
        assert result == expected_user
        user_mock_repository.add_user.assert_called_once_with(user_create)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_user_repository_error(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test add_user when the repository raises UserRepositoryError."""
        # Arrange
        user_create = UserCreate(
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=False,
            hashed_password="hashed-password",
        )
        user_mock_repository.add_user.side_effect = UserRepositoryError("DB error")

        # Act and Assert
        with pytest.raises(UserServiceError):
            await user_service.add_user(user_create)

        user_mock_repository.add_user.assert_called_once_with(user_create)


class TestGetUsers:
    """Tests for UserService.get_users()."""

    @pytest.mark.asyncio
    async def test_get_users_success_with_users(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test successfully retrieving a list of users."""
        # Arrange
        users = [
            User(
                id=1,
                username="alice",
                email="alice@example.com",
                full_name="Alice Smith",
                disabled=False,
            ),
            User(
                id=2,
                username="bob",
                email="bob@example.com",
                full_name="Bob Jones",
                disabled=True,
            ),
        ]
        user_mock_repository.get_users.return_value = users

        # Act
        result = await user_service.get_users()

        # Assert
        assert result == users
        assert len(result) == 2
        user_mock_repository.get_users.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_users_success_empty_list(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test retrieving an empty list of users."""
        # Arrange
        user_mock_repository.get_users.return_value = []

        # Act
        result = await user_service.get_users()

        # Assert
        assert result == []
        user_mock_repository.get_users.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_users_repository_error(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test get_users when the repository raises UserRepositoryError."""
        # Arrange
        user_mock_repository.get_users.side_effect = UserRepositoryError("DB error")

        # Act and Assert
        with pytest.raises(UserServiceError):
            await user_service.get_users()

        user_mock_repository.get_users.assert_called_once()


class TestGetUser:
    """Tests for UserService.get_user()."""

    @pytest.mark.asyncio
    async def test_get_user_success(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test successfully retrieving a user by ID."""
        # Arrange
        user = User(
            id=1,
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
            disabled=False,
        )
        user_mock_repository.get_user.return_value = user

        # Act
        result = await user_service.get_user(user_id=1)

        # Assert
        assert result == user
        user_mock_repository.get_user.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_not_found(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test get_user raises UserNotFoundError when the user does not exist."""
        # Arrange
        user_mock_repository.get_user.return_value = None

        # Act and Assert
        with pytest.raises(UserNotFoundError):
            await user_service.get_user(user_id=999)

        user_mock_repository.get_user.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_get_user_repository_error(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test get_user when the repository raises UserRepositoryError."""
        # Arrange
        user_mock_repository.get_user.side_effect = UserRepositoryError("DB error")

        # Act and Assert
        with pytest.raises(UserServiceError):
            await user_service.get_user(user_id=1)

        user_mock_repository.get_user.assert_called_once_with(1)


class TestUpdateUser:
    """Tests for UserService.update_user()."""

    @pytest.mark.asyncio
    async def test_update_user_success(
        self,
        user_service: UserService,
        user_mock_repository: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test successfully updating a user."""
        # Arrange
        user_update = UserUpdate(full_name="Alice Jones", disabled=True)
        updated_user = User(
            id=1,
            username="alice",
            email="alice@example.com",
            full_name="Alice Jones",
            disabled=True,
        )
        user_mock_repository.update_user.return_value = updated_user

        # Act
        result = await user_service.update_user(user_id=1, payload=user_update)

        # Assert
        assert result == updated_user
        user_mock_repository.update_user.assert_called_once_with(1, user_update)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_not_found(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test update_user raises UserNotFoundError when the user does not exist."""
        # Arrange
        user_update = UserUpdate(full_name="Ghost")
        user_mock_repository.update_user.return_value = None

        # Act and Assert
        with pytest.raises(UserNotFoundError):
            await user_service.update_user(user_id=999, payload=user_update)

        user_mock_repository.update_user.assert_called_once_with(999, user_update)

    @pytest.mark.asyncio
    async def test_update_user_repository_error(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test update_user when the repository raises UserRepositoryError."""
        # Arrange
        user_update = UserUpdate(full_name="Alice Jones")
        user_mock_repository.update_user.side_effect = UserRepositoryError("DB error")

        # Act and Assert
        with pytest.raises(UserServiceError):
            await user_service.update_user(user_id=1, payload=user_update)

        user_mock_repository.update_user.assert_called_once_with(1, user_update)


class TestDeleteUser:
    """Tests for UserService.delete_user()."""

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self,
        user_service: UserService,
        user_mock_repository: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test successfully deleting a user."""
        # Arrange
        user_mock_repository.delete_user.return_value = True

        # Act
        result = await user_service.delete_user(user_id=1)

        # Assert
        assert result is None
        user_mock_repository.delete_user.assert_called_once_with(1)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test delete_user raises UserNotFoundError when the user does not exist."""
        # Arrange
        user_mock_repository.delete_user.return_value = False

        # Act and Assert
        with pytest.raises(UserNotFoundError):
            await user_service.delete_user(user_id=999)

        user_mock_repository.delete_user.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_delete_user_repository_error(
        self, user_service: UserService, user_mock_repository: AsyncMock
    ) -> None:
        """Test delete_user when the repository raises UserRepositoryError."""
        # Arrange
        user_mock_repository.delete_user.side_effect = UserRepositoryError("DB error")

        # Act and Assert
        with pytest.raises(UserServiceError):
            await user_service.delete_user(user_id=1)

        user_mock_repository.delete_user.assert_called_once_with(1)
