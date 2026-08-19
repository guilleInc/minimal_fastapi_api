"""Shared test fixtures for all test suites."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base
from app.repositories.pet_repository import SqlaPetRepository
from app.routes.pet_router import router as pet_router
from app.exception_handlers import register_exception_handlers
from app.services.pet_service import PetService
from app.dependencies import get_pet_service, get_pet_repository, get_db_session


# ============================================================================
# Integration test fixtures (database, session, repository)
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create in-memory SQLite engine for integration tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture()
async def session(engine):
    """Create a new database session for each test."""
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture()
async def repository(session: AsyncSession):
    """Create a repository instance with test session."""
    return SqlaPetRepository(session=session)


# ============================================================================
# Unit test fixtures (mocks and test client)
# ============================================================================


@asynccontextmanager
async def no_lifespan(app: FastAPI):
    """Empty lifespan for testing to avoid DB initialization."""
    yield


@pytest.fixture
def mock_pet_service():
    """Create a mocked PetService for unit tests."""
    return AsyncMock(spec=PetService)


@pytest.fixture
def client(mock_pet_service):
    """Test client with mocked PetService injected."""
    # Create a test app without database lifespan
    test_app = FastAPI(lifespan=no_lifespan)
    register_exception_handlers(test_app)
    test_app.include_router(pet_router)

    # Override the dependency functions, not the types
    test_app.dependency_overrides[get_db_session] = lambda: AsyncMock()
    test_app.dependency_overrides[get_pet_repository] = lambda: AsyncMock()
    test_app.dependency_overrides[get_pet_service] = lambda: mock_pet_service

    client = TestClient(test_app)
    yield client

    test_app.dependency_overrides.clear()

