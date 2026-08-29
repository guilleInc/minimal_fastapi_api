from collections.abc import AsyncGenerator, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session, verify_access_token
from app.exception_handlers import register_exception_handlers
from app.routes.router import router


@pytest.fixture
def authorization_header() -> dict:
    return {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test-payload.test-signature"
    }


@pytest.fixture
def client(session: AsyncSession) -> Iterator[TestClient]:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)

    async def get_db_session_for_test() -> AsyncGenerator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = get_db_session_for_test
    app.dependency_overrides[verify_access_token] = lambda: "test_user"

    with TestClient(app) as client:
        yield client
