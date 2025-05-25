from datetime import datetime
from datetime import timedelta
import os
import secrets
from typing import Any
from typing import AsyncGenerator
from typing import Dict

from fastapi.testclient import TestClient
import jwt
import pytest
import pytest_asyncio
from tortoise.contrib.test import finalizer
from tortoise.contrib.test import initializer

from backend.app import app
from backend.db.models.user import User
from backend.db.models.user_session import UserSession
from backend.utils.auth import create_access_token
from backend.utils.auth import create_refresh_token
from backend.utils.datetime import now_utc
from backend.utils.settings import settings


# Create a module-level event loop for the tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # Close loop explicitly to avoid RuntimeError
    if loop.is_running():
        loop.call_soon_threadsafe(loop.stop)
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(event_loop):
    """Initialize the test database and create required tables."""
    import threading

    db_url = os.environ.get("TEST_DB_URL", "sqlite://:memory:")

    # Initialize the database
    initializer(
        [
            "backend.db.models.user",
            "backend.db.models.user_session",
            "backend.db.models.login_attempt",
            "backend.db.models.user_event",
        ],
        db_url=db_url,
    )

    yield

    # Use threading.Event to track finalizer completion
    done = threading.Event()
    exception = None

    def cleanup():
        nonlocal exception
        try:
            finalizer()
            done.set()
        except Exception as e:
            exception = e
            done.set()

    # Run finalizer in a separate thread
    thread = threading.Thread(target=cleanup)
    thread.daemon = True
    thread.start()

    # Wait for finalizer to complete with a timeout
    if not done.wait(timeout=5.0):
        # If timeout occurs, just continue
        print("Warning: Database cleanup timed out, but tests will continue")

    # If there was an exception, re-raise it
    if exception:
        raise exception


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
    await user.set_password("Password123!")
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
    await user.set_password("AdminPass123!")
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
        expires_at=datetime.utcnow() + timedelta(days=7),
        user_agent="Test Agent",
        ip_address="127.0.0.1",
        is_active=True,
    )
    yield session
    await session.delete()
