"""Service test fixtures."""

from unittest.mock import AsyncMock

import pytest

from app.repositories.pet_repository import PetRepository
from app.repositories.user_repository import UserRepository
from app.services.pet_service import PetService
from app.services.user_service import UserService


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
def user_mock_repository() -> AsyncMock:
    """Create a mock UserRepository."""
    return AsyncMock(spec=UserRepository)


@pytest.fixture()
def user_service(mock_session: AsyncMock, user_mock_repository: AsyncMock) -> UserService:
    """Create a UserService instance with mocked dependencies."""
    return UserService(session=mock_session, user_repository=user_mock_repository)
