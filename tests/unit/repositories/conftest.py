from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pet_model import PetModel
from app.models.user_model import UserModel
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


@pytest_asyncio.fixture(autouse=True)
async def clean_repositories(session: AsyncSession) -> AsyncGenerator[None]:
    """Clean up repository data after each test."""
    yield
    await session.execute(delete(PetModel))
    await session.execute(delete(UserModel))
    await session.commit()
