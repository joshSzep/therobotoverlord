"""Tests for the logout endpoint."""

from typing import Generator
from unittest import mock
import uuid

from fastapi import status
from fastapi.testclient import TestClient
import pytest

from backend.app import app
from backend.db.models.user import User
from backend.db.models.user_session import UserSession
from backend.utils.auth import get_current_user
from backend.utils.constants import UNKNOWN_IP_ADDRESS_MARKER


@pytest.fixture
def mock_user() -> User:
    """Return a mock user for testing."""
    user_id = uuid.uuid4()

    mock_user = mock.MagicMock(spec=User)
    mock_user.id = user_id
    return mock_user


@pytest.fixture
def mock_active_session() -> UserSession:
    """Return a mock active user session."""
    session = mock.MagicMock(spec=UserSession)
    session.is_active = True
    session.invalidate = mock.AsyncMock()
    return session


@pytest.fixture
def client(mock_user: User) -> Generator[TestClient, None, None]:
    """Return a TestClient instance with overridden dependencies."""

    # Override the get_current_user dependency
    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    # Yield the test client
    client = TestClient(app)
    yield client

    # Clean up after test
    app.dependency_overrides = {}


def test_logout_with_active_session(
    client: TestClient,
    mock_user: User,
    mock_active_session: UserSession,
) -> None:
    """Test logout when user has one active session matching IP and User-Agent."""
    # Mock user.sessions.filter().all() to return one active session
    mock_filter = mock.AsyncMock()
    mock_filter.all.return_value = [mock_active_session]
    mock_user.sessions.filter.return_value = mock_filter

    # Mock UserEvent.log_logout
    with mock.patch(
        "backend.db.models.user_event.UserEvent.log_logout",
        new_callable=mock.AsyncMock,
    ) as mock_log_logout:
        # Call the endpoint
        response = client.post("/users/profile/logout")

        # Verify status code
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify mocks were called correctly
        mock_user.sessions.filter.assert_called_once_with(
            ip_address=mock.ANY,
            user_agent=mock.ANY,
            is_active=True,
        )
        mock_active_session.invalidate.assert_awaited_once()
        mock_log_logout.assert_awaited_once_with(
            mock_user.id,
            mock.ANY,  # IP address
            mock.ANY,  # User agent
        )


def test_logout_with_multiple_active_sessions(
    client: TestClient,
    mock_user: User,
) -> None:
    """Test logout when user has multiple active sessions matching IP and User-Agent."""
    # Create multiple active sessions
    session1 = mock.MagicMock(spec=UserSession)
    session1.is_active = True
    session1.invalidate = mock.AsyncMock()

    session2 = mock.MagicMock(spec=UserSession)
    session2.is_active = True
    session2.invalidate = mock.AsyncMock()

    # Mock user.sessions.filter().all() to return multiple active sessions
    mock_filter = mock.AsyncMock()
    mock_filter.all.return_value = [session1, session2]
    mock_user.sessions.filter.return_value = mock_filter

    # Mock UserEvent.log_logout
    with mock.patch(
        "backend.db.models.user_event.UserEvent.log_logout",
        new_callable=mock.AsyncMock,
    ) as mock_log_logout:
        # Call the endpoint
        response = client.post("/users/profile/logout")

        # Verify status code
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify both sessions were invalidated
        session1.invalidate.assert_awaited_once()
        session2.invalidate.assert_awaited_once()
        mock_log_logout.assert_awaited_once()


def test_logout_with_no_matching_sessions(
    client: TestClient,
    mock_user: User,
) -> None:
    """Test logout with no matching active sessions."""
    # No matching sessions for current client info
    # Mock user.sessions.filter().all() to return empty list
    mock_filter = mock.AsyncMock()
    mock_filter.all.return_value = []
    mock_user.sessions.filter.return_value = mock_filter

    # Mock UserEvent.log_logout
    with mock.patch(
        "backend.db.models.user_event.UserEvent.log_logout",
        new_callable=mock.AsyncMock,
    ) as mock_log_logout:
        # Call the endpoint
        response = client.post("/users/profile/logout")

        # Verify status code
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify log_logout was still called even with no sessions to invalidate
        mock_log_logout.assert_awaited_once_with(
            mock_user.id,
            mock.ANY,
            mock.ANY,
        )


def test_logout_with_no_client_info(
    client: TestClient,
    mock_user: User,
) -> None:
    """Test logout when request.client is None."""
    # Mock user.sessions.filter().all() to return an empty list
    mock_filter = mock.AsyncMock()
    mock_filter.all.return_value = []
    mock_user.sessions.filter.return_value = mock_filter

    # Mock UserEvent.log_logout and request.client to be None
    with (
        mock.patch(
            "backend.db.models.user_event.UserEvent.log_logout",
            new_callable=mock.AsyncMock,
        ) as mock_log_logout,
        mock.patch(
            "fastapi.Request.client",
            new_callable=mock.PropertyMock,
            return_value=None,
        ),
    ):
        # Call the endpoint
        response = client.post("/users/profile/logout")

        # Verify status code
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify UserEvent.log_logout was called with UNKNOWN_IP_ADDRESS_MARKER
        mock_log_logout.assert_awaited_once_with(
            mock_user.id,
            UNKNOWN_IP_ADDRESS_MARKER,
            mock.ANY,  # User agent
        )

        # Verify sessions.filter was called with UNKNOWN_IP_ADDRESS_MARKER
        mock_user.sessions.filter.assert_called_once_with(
            ip_address=UNKNOWN_IP_ADDRESS_MARKER,
            user_agent=mock.ANY,
            is_active=True,
        )


def test_logout_with_no_user_agent(
    client: TestClient,
    mock_user: User,
) -> None:
    """Test logout when User-Agent header is missing."""
    # Mock user.sessions.filter().all() to return an empty list
    mock_filter = mock.AsyncMock()
    mock_filter.all.return_value = []
    mock_user.sessions.filter.return_value = mock_filter

    # Mock UserEvent.log_logout
    with mock.patch(
        "backend.db.models.user_event.UserEvent.log_logout",
        new_callable=mock.AsyncMock,
    ) as mock_log_logout:
        # Call the endpoint without User-Agent header
        response = client.post(
            "/users/profile/logout",
            headers={"User-Agent": ""},  # Empty User-Agent
        )

        # Verify status code
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify UserEvent.log_logout was called with empty user_agent
        call_args = mock_log_logout.await_args[0]
        assert call_args[0] == mock_user.id  # user_id
        assert call_args[2] == ""  # user_agent (empty string)

        # Verify sessions.filter was called with empty user_agent
        filter_kwargs = mock_user.sessions.filter.call_args[1]
        assert filter_kwargs["user_agent"] == ""
