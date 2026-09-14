from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.pet_repository import PetRepository
from app.repositories.user_repository import UserRepository
from app.security.password_hasher import PasswordHasher
from app.security.token_manager import TokenManager
from app.services.auth_service import AuthService
from app.services.pet_service import PetService


@pytest.fixture()
def mock_session() -> AsyncMock:
    """Create a mock AsyncSession."""
    session = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture()
def mock_repository() -> AsyncMock:
    """Create a mock PetRepository."""
    return AsyncMock(spec=PetRepository)


@pytest.fixture
def service(mock_session: AsyncMock, mock_repository: AsyncMock) -> PetService:
    """Create a PetService instance with mocked dependencies."""
    return PetService(session=mock_session, pet_repository=mock_repository)


@pytest.fixture()
def mock_token_manager() -> MagicMock:
    """Create a mock TokenManager."""
    return MagicMock(spec=TokenManager)


@pytest.fixture()
def mock_password_hasher() -> MagicMock:
    """Create a mock PasswordHasher."""
    return MagicMock(spec=PasswordHasher)


@pytest.fixture()
def auth_service(
    mock_token_manager: MagicMock,
    mock_password_hasher: MagicMock,
) -> AuthService:
    """Create an AuthService instance with mocked dependencies."""
    user_repository = AsyncMock(spec=UserRepository)
    return AuthService(
        token_manager=mock_token_manager,
        password_hasher=mock_password_hasher,
        user_repository=user_repository,
    )
