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

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.profile.logout.deactivate_all_user_sessions",
            new=mock.AsyncMock(),
        ) as mock_deactivate_all_sessions,
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
        mock_deactivate_all_sessions.assert_called_once_with(user_id)
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

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.profile.logout.deactivate_all_user_sessions",
            new=mock.AsyncMock(return_value=2),  # Return count of deactivated sessions
        ) as mock_deactivate_all_sessions,
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
        mock_deactivate_all_sessions.assert_called_once_with(user_id)
        mock_log_logout.assert_called_once_with(
            user_id, mock_request.client.host, mock_request.headers.get("User-Agent")
        )


@pytest.mark.asyncio
async def test_logout_no_matching_sessions():
    """Test logout with no active sessions."""
    # Arrange
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id

    # Create mock request
    mock_request = mock.MagicMock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test User Agent"}

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.profile.logout.deactivate_all_user_sessions",
            new=mock.AsyncMock(return_value=0),  # Return 0 deactivated sessions
        ) as mock_deactivate_all_sessions,
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
        mock_deactivate_all_sessions.assert_called_once_with(user_id)
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

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.profile.logout.deactivate_all_user_sessions",
            new=mock.AsyncMock(),
        ) as mock_deactivate_all_sessions,
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
        mock_deactivate_all_sessions.assert_called_once_with(user_id)
        mock_log_logout.assert_called_once_with(user_id, UNKNOWN_IP_ADDRESS_MARKER, "")
