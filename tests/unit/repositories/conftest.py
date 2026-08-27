import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.pet_repository import SqlaPetRepository
from app.repositories.user_repository import SqlaUserRepository


@pytest.fixture()
def pet_repository(session: AsyncSession) -> SqlaPetRepository:
    """Create a pet repository instance with test session."""
    return SqlaPetRepository(session=session)


@pytest.fixture()
def user_repository(session: AsyncSession) -> SqlaUserRepository:
    """Create a user repository instance with test session."""
    return SqlaUserRepository(session=session)
