"""Repository test fixtures."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.pet_repository import SqlaPetRepository


@pytest.fixture()
def repository(session: AsyncSession):
    """Create a repository instance with test session."""
    return SqlaPetRepository(session=session)
