"""
Pytest configuration for E2E tests.
"""

import asyncio
import io
import os
import re
import time
from typing import AsyncGenerator
from typing import Callable
from typing import Dict
from typing import Generator
from typing import List
from typing import Pattern
import uuid

import httpx
import pytest
import pytest_asyncio
from tortoise import Tortoise


# Define a marker to disable server error detection for specific tests
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "ignore_server_errors: mark test to ignore server errors"
    )


# Constants
API_HOST = "localhost"
API_PORT = 8000
API_URL = f"http://{API_HOST}:{API_PORT}"

# Error whitelist patterns - these errors will not cause tests to fail
# Each pattern is a regular expression that will be matched against log messages
WHITELISTED_ERROR_PATTERNS: List[Pattern] = [
    # Example: re.compile(r"Expected error from third-party library"),
    # Add specific patterns here as needed
    re.compile(r"Example whitelisted error pattern"),  # This is just an example
]

# Configure database settings for tests
# Use an in-memory SQLite database for E2E tests for faster execution
TEST_DB_URL = "sqlite://:memory:"

# Set environment variables for testing
# These will be used by the database configuration in config.py
os.environ["TESTING"] = "True"
os.environ["DB_ENGINE"] = "sqlite"
os.environ["DATABASE_URL"] = TEST_DB_URL

# Global variable to store server logs
server_log_stream = io.StringIO()


def get_server_logs() -> str:
    """Get the current server logs.

    This is useful for debugging server errors in tests.
    """
    return server_log_stream.getvalue()


@pytest.fixture(autouse=True)
def server_logs() -> Generator[Callable[[], str], None, None]:
    """Fixture that provides access to server logs.

    This fixture is automatically applied to all tests (autouse=True).
    It clears the log stream at the start of each test and provides
    a function that returns the current server logs.

    Returns:
        callable: A function that returns the current server logs
    """
    # Clear the log stream at the start of each test
    server_log_stream.truncate(0)
    server_log_stream.seek(0)

    # Let the test run
    yield get_server_logs

    # No cleanup needed, logs will be cleared at the start of the next test


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Pytest hook to check for server errors after each test.

    This will run after each test and check for:
    1. Any ERROR level logs in the server logs
    2. Any 500 status codes in responses

    If errors are found, it will print detailed information to help diagnose the issue.
    """
    outcome = yield
    result = outcome.get_result()

    # Only check for errors after the test has run (not during setup/teardown)
    if result.when == "call":
        # Skip error detection if the test is marked to ignore server errors
        if item.get_closest_marker("ignore_server_errors") is not None:
            return

        has_server_error = False
        error_message = ""

        # Get the server_logs fixture if it's available
        server_logs_fixture = item.funcargs.get("server_logs")
        if server_logs_fixture:
            logs = server_logs_fixture()
            if "ERROR" in logs:
                # Check if the error is whitelisted
                is_whitelisted = False
                for pattern in WHITELISTED_ERROR_PATTERNS:
                    if pattern.search(logs):
                        is_whitelisted = True
                        break

                if not is_whitelisted:
                    has_server_error = True
                    test_name = item.name
                    error_message = (
                        f"\n\n=== UNEXPECTED SERVER ERROR IN TEST {test_name} ===\n"
                    )
                    error_message += "\n=== SERVER LOGS ===\n"
                    error_message += logs
                    error_message += "\n=== END SERVER LOGS ===\n"
                    print(error_message)

        # Check for 500 status codes in the test result
        if (
            hasattr(call, "excinfo")
            and call.excinfo is None
            and hasattr(result, "sections")
        ):
            for section_name, section_content in result.sections:
                if "response" in section_name.lower() and "500" in section_content:
                    has_server_error = True
                    test_name = item.name
                    status_error = (
                        f"\n\n=== 500 STATUS CODE DETECTED IN TEST {test_name} ===\n"
                    )
                    status_error += f"Response: {section_content}"

                    if server_logs_fixture:
                        logs = server_logs_fixture()
                        status_error += "\n=== SERVER LOGS ===\n"
                        status_error += logs
                        status_error += "\n=== END SERVER LOGS ===\n"

                    # Add to or set the error message
                    if error_message:
                        error_message += "\n" + status_error
                    else:
                        error_message = status_error

                    print(status_error)

        # Fail the test if server errors were detected
        if has_server_error:
            # Use pytest's internal mechanism to fail the test
            pytest.fail(f"Server error detected:\n{error_message}")


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
    import logging
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

    # Set up logging to capture server errors
    log_handler = logging.StreamHandler(server_log_stream)
    log_handler.setLevel(logging.ERROR)  # Capture ERROR and above
    logging.getLogger("uvicorn").addHandler(log_handler)
    logging.getLogger("uvicorn.error").addHandler(log_handler)
    logging.getLogger("fastapi").addHandler(log_handler)

    # Configure Uvicorn with access to logs
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
