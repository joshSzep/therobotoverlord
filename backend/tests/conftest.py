# Standard library imports
from datetime import timedelta
import os
import secrets
from typing import Any
from typing import AsyncGenerator
from typing import Dict

# Third-party imports
from fastapi.testclient import TestClient
import jwt
import pytest
import pytest_asyncio
from tortoise import Tortoise

# Project-specific imports
from backend.app import app
from backend.db import close_db
from backend.db import init_db
from backend.db.models.user import User
from backend.db.models.user_session import UserSession
from backend.utils.auth import create_access_token
from backend.utils.auth import create_refresh_token
from backend.utils.datetime import now_utc
from backend.utils.settings import settings


@pytest.fixture(scope="session")
def db_url():
    """Get the test database URL."""
    return os.environ.get("TEST_DB_URL", "sqlite://:memory:")


@pytest_asyncio.fixture(scope="function", autouse=True)
async def initialize_tests(db_url):
    """Initialize the test database and create required tables."""
    # Initialize the database using the app's init_db function
    await init_db(db_url=db_url)

    # Generate schemas for all apps
    await Tortoise.generate_schemas()

    yield

    # Close all connections using the app's close_db function
    await close_db()


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest_asyncio.fixture
async def test_user() -> AsyncGenerator[User, None]:
    """Create a test user for authentication tests."""
    user_data: Dict[str, Any] = {
        "email": "test@example.com",
        "display_name": "Test User",
    }
    user = await User.create(**user_data)
    # Use the db_function instead of a model method
    from backend.db_functions.users.set_user_password import set_user_password

    await set_user_password(user.id, "Password123!")
    yield user
    await user.delete()


@pytest_asyncio.fixture
async def admin_user() -> AsyncGenerator[User, None]:
    """Create an admin test user for authentication tests."""
    user_data: Dict[str, Any] = {
        "email": "admin@example.com",
        "display_name": "Admin User",
        "is_admin": True,
    }
    user = await User.create(**user_data)
    # Use the db_function instead of a model method
    from backend.db_functions.users.set_user_password import set_user_password

    await set_user_password(user.id, "AdminPass123!")
    yield user
    await user.delete()


@pytest_asyncio.fixture
async def test_user_token(test_user: User) -> str:
    """Create a JWT access token for the test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest_asyncio.fixture
async def test_user_refresh_token(test_user: User) -> str:
    """Create a JWT refresh token for the test user."""
    return create_refresh_token(data={"sub": str(test_user.id)})


@pytest_asyncio.fixture
async def expired_token(test_user: User) -> str:
    """Create an expired JWT token for testing."""
    to_encode: Dict[str, Any] = {"sub": str(test_user.id)}
    expire = now_utc() - timedelta(minutes=30)
    to_encode["exp"] = int(expire.timestamp())
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


@pytest.fixture
def invalid_token() -> str:
    """Create an invalid JWT token for testing."""
    return "invalid.token.format"


@pytest_asyncio.fixture
async def test_user_session(test_user: User) -> AsyncGenerator[UserSession, None]:
    """Create a test user session."""
    session = await UserSession.create(
        user=test_user,
        session_token=secrets.token_hex(32),
        expires_at=now_utc() + timedelta(days=7),
        user_agent="Test Agent",
        ip_address="127.0.0.1",
        is_active=True,
    )
    yield session
    await session.delete()
