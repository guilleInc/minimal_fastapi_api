"""Service test fixtures."""

import pytest
from unittest.mock import AsyncMock

from app.repositories.pet_repository import PetRepository


@pytest.fixture()
def mock_session():
    """Create a mock AsyncSession."""
    session = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture()
def mock_repository():
    """Create a mock PetRepository."""
    return AsyncMock(spec=PetRepository)
