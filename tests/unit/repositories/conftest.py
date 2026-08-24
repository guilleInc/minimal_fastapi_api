import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.repositories.pet_repository import SqlaPetRepository
from app.models.pet_model import PetModel


@pytest.fixture()
def repository(session: AsyncSession):
    """Create a repository instance with test session."""
    return SqlaPetRepository(session=session)

@pytest_asyncio.fixture(autouse=True)
async def clean_pets(session):
    """Clean up pets after each test."""
    yield
    await session.execute(delete(PetModel))
    await session.commit()
