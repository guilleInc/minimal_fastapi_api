"""Integration test configuration with transaction rollback."""

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.exception_handlers import register_exception_handlers
from app.routes.pet_router import router as pet_router


@pytest_asyncio.fixture()
async def session(engine):
    """Create a test session wrapped in a transaction.

    All session.commit() calls are staged to this transaction.
    At test end, the entire transaction is rolled back,
    leaving the database clean for the next test.
    """
    connection = await engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)
    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture()
async def test_app(session):
    """Create FastAPI app with test session injected."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(pet_router)

    # Override dependencies to use test session
    async def override_get_db_session():
        yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    yield app

    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def client(test_app):
    """AsyncClient for making requests to test app."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as http_client:
        yield http_client
