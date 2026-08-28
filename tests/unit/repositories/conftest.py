import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.pet_repository import SqlaPetRepository


@pytest.fixture()
def pet_repository(session: AsyncSession) -> SqlaPetRepository:
    """Create a pet repository instance with test session."""
    return SqlaPetRepository(session=session)
