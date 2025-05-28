# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import Request
import pytest

# Project-specific imports
from backend.routes.profile.logout import logout
from backend.utils.constants import UNKNOWN_IP_ADDRESS_MARKER


@pytest.mark.asyncio
async def test_logout_success():
    """Test successful logout."""
    # Arrange
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id

    # Create mock request
    mock_request = mock.MagicMock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test User Agent"}

    # Create mock session
    mock_session = mock.MagicMock()
    mock_session.session_token = "test-session-token"
    mock_session.ip_address = "127.0.0.1"
    mock_session.user_agent = "Test User Agent"

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.profile.logout.list_user_sessions",
            new=mock.AsyncMock(return_value=([mock_session], 1)),
        ) as mock_list_sessions,
        mock.patch(
            "backend.routes.profile.logout.deactivate_session",
            new=mock.AsyncMock(),
        ) as mock_deactivate_session,
        mock.patch(
            "backend.routes.profile.logout.log_logout",
            new=mock.AsyncMock(),
        ) as mock_log_logout,
    ):
        # Act
        result = await logout(
            request=mock_request,
            current_user=mock_user,
        )

        # Assert
        assert result is None  # Function returns None on success

        # Verify function calls
        mock_list_sessions.assert_called_once_with(
            user_id=user_id,
            active_only=True,
        )
        mock_deactivate_session.assert_called_once_with(mock_session.session_token)
        mock_log_logout.assert_called_once_with(
            user_id, mock_request.client.host, mock_request.headers.get("User-Agent")
        )


@pytest.mark.asyncio
async def test_logout_multiple_sessions():
    """Test logout with multiple sessions."""
    # Arrange
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id

    # Create mock request
    mock_request = mock.MagicMock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test User Agent"}

    # Create mock sessions - one matching, one non-matching
    mock_session1 = mock.MagicMock()
    mock_session1.session_token = "test-session-token-1"
    mock_session1.ip_address = "127.0.0.1"
    mock_session1.user_agent = "Test User Agent"

    mock_session2 = mock.MagicMock()
    mock_session2.session_token = "test-session-token-2"
    mock_session2.ip_address = "192.168.1.1"  # Different IP
    mock_session2.user_agent = "Different User Agent"  # Different user agent

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.profile.logout.list_user_sessions",
            new=mock.AsyncMock(return_value=([mock_session1, mock_session2], 2)),
        ) as mock_list_sessions,
        mock.patch(
            "backend.routes.profile.logout.deactivate_session",
            new=mock.AsyncMock(),
        ) as mock_deactivate_session,
        mock.patch(
            "backend.routes.profile.logout.log_logout",
            new=mock.AsyncMock(),
        ) as mock_log_logout,
    ):
        # Act
        result = await logout(
            request=mock_request,
            current_user=mock_user,
        )

        # Assert
        assert result is None  # Function returns None on success

        # Verify function calls
        mock_list_sessions.assert_called_once_with(
            user_id=user_id,
            active_only=True,
        )
        # Only the matching session should be deactivated
        mock_deactivate_session.assert_called_once_with(mock_session1.session_token)
        mock_log_logout.assert_called_once_with(
            user_id, mock_request.client.host, mock_request.headers.get("User-Agent")
        )


@pytest.mark.asyncio
async def test_logout_no_matching_sessions():
    """Test logout with no matching sessions."""
    # Arrange
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id

    # Create mock request
    mock_request = mock.MagicMock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test User Agent"}

    # Create mock session with non-matching IP and user agent
    mock_session = mock.MagicMock()
    mock_session.session_token = "test-session-token"
    mock_session.ip_address = "192.168.1.1"  # Different IP
    mock_session.user_agent = "Different User Agent"  # Different user agent

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.profile.logout.list_user_sessions",
            new=mock.AsyncMock(return_value=([mock_session], 1)),
        ) as mock_list_sessions,
        mock.patch(
            "backend.routes.profile.logout.deactivate_session",
            new=mock.AsyncMock(),
        ) as mock_deactivate_session,
        mock.patch(
            "backend.routes.profile.logout.log_logout",
            new=mock.AsyncMock(),
        ) as mock_log_logout,
    ):
        # Act
        result = await logout(
            request=mock_request,
            current_user=mock_user,
        )

        # Assert
        assert result is None  # Function returns None on success

        # Verify function calls
        mock_list_sessions.assert_called_once_with(
            user_id=user_id,
            active_only=True,
        )
        # No sessions should be deactivated
        mock_deactivate_session.assert_not_called()
        mock_log_logout.assert_called_once_with(
            user_id, mock_request.client.host, mock_request.headers.get("User-Agent")
        )


@pytest.mark.asyncio
async def test_logout_missing_client_info():
    """Test logout with missing client information."""
    # Arrange
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id

    # Create mock request with missing client info
    mock_request = mock.MagicMock(spec=Request)
    mock_request.client = None
    mock_request.headers = {}

    # Create mock session
    mock_session = mock.MagicMock()
    mock_session.session_token = "test-session-token"
    mock_session.ip_address = UNKNOWN_IP_ADDRESS_MARKER
    mock_session.user_agent = ""

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.profile.logout.list_user_sessions",
            new=mock.AsyncMock(return_value=([mock_session], 1)),
        ) as mock_list_sessions,
        mock.patch(
            "backend.routes.profile.logout.deactivate_session",
            new=mock.AsyncMock(),
        ) as mock_deactivate_session,
        mock.patch(
            "backend.routes.profile.logout.log_logout",
            new=mock.AsyncMock(),
        ) as mock_log_logout,
    ):
        # Act
        result = await logout(
            request=mock_request,
            current_user=mock_user,
        )

        # Assert
        assert result is None  # Function returns None on success

        # Verify function calls with fallback values
        mock_list_sessions.assert_called_once_with(
            user_id=user_id,
            active_only=True,
        )
        mock_deactivate_session.assert_called_once_with(mock_session.session_token)
        mock_log_logout.assert_called_once_with(user_id, UNKNOWN_IP_ADDRESS_MARKER, "")
