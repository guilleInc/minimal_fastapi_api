from collections.abc import AsyncGenerator, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.exception_handlers import register_exception_handlers
from app.routes.pet_router import router as pet_router


@pytest.fixture
def client(session: AsyncSession) -> Iterator[TestClient]:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(pet_router)

    async def get_db_session_for_test() -> AsyncGenerator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = get_db_session_for_test

    with TestClient(app) as client:
        yield client
