import os
import sys
from sqlalchemy import text
from sqlalchemy.pool import NullPool
import asyncio
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx import ASGITransport
from asgi_lifespan import LifespanManager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from dotenv import load_dotenv
load_dotenv()

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# --- Environment guards for TEST DB ---
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not set. Configure it before running tests.")
if "test" not in TEST_DATABASE_URL.lower():
    raise RuntimeError(f"TEST_DATABASE_URL must point to a *test* database, got: {TEST_DATABASE_URL}")

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# Import FastAPI app and route modules
from app.main import app as fastapi_app
from app.db.base import Base
from app.api import product_routes, category_routes, department_routes
import app.models  # Ensure models are registered

# Create async engine & session factory for tests
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    future=True,
    poolclass=NullPool,
)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    """Provide a single event loop for the whole test session (Windows safe)."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def prepare_database():
    """Ensure a pristine schema for the whole test session."""
    async with test_engine.begin() as conn:
        # Nuke and recreate the 'public' schema to avoid duplicate index errors
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.execute(text("SET search_path TO public;"))
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))

async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a test session for route dependencies."""
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture(autouse=True)
def override_dependencies():
    """Override per-module get_db to use the test session."""
    fastapi_app.dependency_overrides[product_routes.get_db] = _get_test_db
    fastapi_app.dependency_overrides[category_routes.get_db] = _get_test_db
    fastapi_app.dependency_overrides[department_routes.get_db] = _get_test_db
    yield
    fastapi_app.dependency_overrides.clear()

try:
    from app.core.cache import cache
except Exception:
    cache = None

@pytest_asyncio.fixture(autouse=True)
async def clear_cache_between_tests():
    """Invalidate in-memory cache between tests to avoid cross-test pollution."""
    if cache and hasattr(cache, "invalidate_prefix"):
        await cache.invalidate_prefix("")
    yield
    if cache and hasattr(cache, "invalidate_prefix"):
        await cache.invalidate_prefix("")

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_client(prepare_database):
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def _db_clean_before_each_test(prepare_database):
    async with test_engine.begin() as conn:
        await conn.execute(
            text("TRUNCATE TABLE products, categories, departments RESTART IDENTITY CASCADE;")
        )
    yield