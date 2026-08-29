from collections.abc import AsyncGenerator, Iterator
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session, get_settings
from app.exception_handlers import register_exception_handlers
from app.routes.router import router
from app.security.token_manager import TokenManager
from app.settings import Settings


@pytest.fixture
def test_settings() -> Mock:
    settings = Mock(spec=Settings)
    settings.jwt_secret_key = "integration-test-jwt-secret-key7f3c9a2d1e6b4f8a0c5d9e2b6a1f7c3d"
    settings.jwt_algorithm = "HS256"
    return settings


@pytest.fixture
def test_access_token(test_settings: Mock) -> str:
    token_manager = TokenManager(
        secret_key=test_settings.jwt_secret_key,
        algorithm=test_settings.jwt_algorithm,
    )
    return token_manager.create_access_token({"user": "test_user"})


@pytest.fixture
def valid_headers(test_access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {test_access_token}"}


@pytest.fixture
def invalid_headers() -> dict[str, str]:
    return {"Authorization": "Bearer invalid-access-token"}


@pytest.fixture
def client(
    session: AsyncSession,
    test_settings: Mock,
) -> Iterator[TestClient]:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)

    async def get_db_session_for_test() -> AsyncGenerator[AsyncSession]:
        yield session

    app.dependency_overrides[get_settings] = lambda: test_settings
    app.dependency_overrides[get_db_session] = get_db_session_for_test
    with TestClient(app) as client:
        yield client
