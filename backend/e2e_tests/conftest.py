"""
Pytest configuration for E2E tests.
"""

import asyncio
import os
import time
from typing import AsyncGenerator
from typing import Dict
from typing import Generator
import uuid

import httpx
import pytest
import pytest_asyncio
from tortoise import Tortoise

# Constants
API_HOST = "localhost"
API_PORT = 8000
API_URL = f"http://{API_HOST}:{API_PORT}"
# Use an in-memory SQLite database for E2E tests for faster execution
TEST_DB_URL = "sqlite://:memory:"

# Set environment variables for testing
os.environ["TESTING"] = "True"
os.environ["DB_ENGINE"] = "sqlite"
os.environ["DATABASE_URL"] = TEST_DB_URL


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def server() -> Generator[None, None, None]:
    """Start the API server programmatically for testing."""

    # Import the app here to ensure environment variables are set before import
    import importlib.util
    import sys
    import threading

    import uvicorn
    from uvicorn.config import Config

    # Import the FastAPI app
    app_path = "/Users/joshszep/code/therobotoverlord/backend/src/backend/app.py"
    spec = importlib.util.spec_from_file_location("app", app_path)
    if spec is None:
        raise ImportError(f"Could not load spec for module at {app_path}")

    app_module = importlib.util.module_from_spec(spec)
    sys.modules["app"] = app_module
    if spec.loader is None:
        raise ImportError(f"Module spec has no loader for {app_path}")

    spec.loader.exec_module(app_module)
    app = app_module.app

    # Configure Uvicorn
    config = Config(app=app, host=API_HOST, port=API_PORT, log_level="debug")
    server = uvicorn.Server(config=config)

    # Run the server in a separate thread
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()

    # Wait for the server to start
    print("Waiting for server to start...")
    max_retries = 10
    for i in range(max_retries):
        try:
            # Try to connect to the server
            response = httpx.get(f"{API_URL}/health/check/")
            if response.status_code == 200:
                print(f"Server is up after {i + 1} attempts")
                break
        except httpx.ConnectError:
            print(f"Connection attempt {i + 1} failed, retrying...")
            time.sleep(1)
    else:
        # If we couldn't connect after all attempts, raise an error
        raise RuntimeError("Failed to start the server after multiple attempts")

    # Yield control back to the tests
    yield

    # Server will automatically shut down when the thread exits


@pytest_asyncio.fixture(scope="function")
async def setup_test_db() -> AsyncGenerator[None, None]:
    """Set up the test database using an in-memory SQLite database.

    This creates a fresh database for each test, ensuring complete isolation.
    """

    # Import here to ensure environment variables are set before import
    from backend.db.config import close_db
    from backend.db.config import init_db

    # Initialize the database with our application's init_db function
    await init_db(TEST_DB_URL)

    # Generate schemas for all models
    await Tortoise.generate_schemas(safe=True)

    yield

    # Close the connection after the test
    await close_db()


@pytest_asyncio.fixture(scope="function")
async def api_client(
    server, setup_test_db: None
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create a test client for making API requests.

    This fixture depends on:
    - server: Ensures the API server is running
    - setup_test_db: Resets the database for each test
    """
    async with httpx.AsyncClient(base_url=API_URL, timeout=10.0) as client:
        yield client


@pytest_asyncio.fixture
async def test_user(api_client: httpx.AsyncClient) -> Dict:
    """Create a test user and return user data."""
    # Generate unique user data
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "email": f"test-user-{unique_id}@example.com",
        "password": "Password123!",
        "display_name": f"Test User {unique_id}",
    }

    # Register the user
    response = await api_client.post("/auth/register/", json=user_data)
    assert response.status_code == 201

    # Return user data and response
    return {
        "user_data": user_data,
        "user_id": response.json()["id"],
        "response": response.json(),
    }


@pytest_asyncio.fixture
async def authenticated_client(
    api_client: httpx.AsyncClient, test_user: Dict
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an authenticated client with a valid token."""
    # Login to get tokens
    login_data = {
        "email": test_user["user_data"]["email"],
        "password": test_user["user_data"]["password"],
    }
    response = await api_client.post("/auth/login/", json=login_data)
    assert response.status_code == 200

    # Get the access token
    token_data = response.json()
    access_token = token_data["access_token"]

    # Create a new client with the authorization header
    async with httpx.AsyncClient(
        base_url=API_URL,
        timeout=10.0,
        headers={"Authorization": f"Bearer {access_token}"},
    ) as auth_client:
        yield auth_client
