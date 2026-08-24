from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pet_model import PetModel
from app.repositories.pet_repository import SqlaPetRepository


@pytest.fixture()
def repository(session: AsyncSession) -> SqlaPetRepository:
    """Create a repository instance with test session."""
    return SqlaPetRepository(session=session)


@pytest_asyncio.fixture(autouse=True)
async def clean_pets(session: AsyncSession) -> AsyncGenerator[None]:
    """Clean up pets after each test."""
    yield
    await session.execute(delete(PetModel))
    await session.commit()
