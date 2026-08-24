"""Service test fixtures."""

from unittest.mock import AsyncMock

import pytest

from app.repositories.pet_repository import PetRepository
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
    return PetService(session=mock_session, repository=mock_repository)
