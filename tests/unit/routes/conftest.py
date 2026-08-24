from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.dependencies import get_db_session, get_pet_repository, get_pet_service
from app.exception_handlers import register_exception_handlers
from app.routes.pet_router import router as pet_router
from app.services.pet_service import PetService


@asynccontextmanager
async def no_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Empty lifespan for testing to avoid DB initialization."""
    yield


@pytest.fixture
def mock_pet_service() -> AsyncMock:
    """Create a mocked PetService."""
    return AsyncMock(spec=PetService)


@pytest.fixture
def client(mock_pet_service: AsyncMock) -> Iterator[TestClient]:
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
