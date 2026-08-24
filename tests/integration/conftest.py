"""Integration test configuration with transaction rollback."""

import asyncio
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.exception_handlers import register_exception_handlers
from app.routes.pet_router import router as pet_router


@pytest.fixture
def session(engine):
    """Create a test session wrapped in a transaction.

    All session.commit() calls are staged to this transaction.
    At test end, the entire transaction is rolled back,
    leaving the database clean for the next test.
    """
    # Run async setup in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        connection = loop.run_until_complete(engine.connect())
        transaction = loop.run_until_complete(connection.begin())

        session = AsyncSession(bind=connection, expire_on_commit=False)
        
        yield session

        loop.run_until_complete(session.close())
        loop.run_until_complete(transaction.rollback())
        loop.run_until_complete(connection.close())
    finally:
        loop.close()
        asyncio.set_event_loop(None)


@pytest.fixture
def test_app(session):
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


@pytest.fixture
def client(test_app):
    """TestClient for making requests to test app."""
    return TestClient(test_app)
