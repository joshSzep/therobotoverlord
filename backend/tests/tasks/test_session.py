# Standard library imports
import asyncio
from unittest import mock

# Third-party imports
import pytest

# Project-specific imports
from backend.tasks.session import cleanup_expired_sessions
from backend.tasks.session import run_session_cleanup_task


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_success():
    """Test successful cleanup of expired sessions."""
    # Arrange
    mock_count = 5

    # Mock dependencies
    with (
        mock.patch("backend.tasks.session.Tortoise") as mock_tortoise,
        mock.patch(
            "backend.tasks.session.db_cleanup_expired_sessions"
        ) as mock_db_cleanup,
        mock.patch("backend.tasks.session.logger") as mock_logger,
    ):
        # Configure mocks
        type(mock_tortoise).init = mock.AsyncMock()
        type(mock_tortoise).close_connections = mock.AsyncMock()
        type(mock_tortoise)._inited = mock.PropertyMock(side_effect=[False, True])
        mock_db_cleanup.return_value = mock_count

        # Act
        result = await cleanup_expired_sessions()

        # Assert
        assert result == mock_count
        mock_tortoise.init.assert_awaited_once()
        mock_db_cleanup.assert_awaited_once()
        mock_tortoise.close_connections.assert_awaited_once()
        mock_logger.info.assert_called_once_with(
            f"Cleaned up {mock_count} expired sessions"
        )


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_no_results():
    """Test cleanup of expired sessions with no results."""
    # Arrange
    mock_count = 0

    # Mock dependencies
    with (
        mock.patch("backend.tasks.session.Tortoise") as mock_tortoise,
        mock.patch(
            "backend.tasks.session.db_cleanup_expired_sessions"
        ) as mock_db_cleanup,
        mock.patch("backend.tasks.session.logger") as mock_logger,
    ):
        # Configure mocks
        type(mock_tortoise).init = mock.AsyncMock()
        type(mock_tortoise).close_connections = mock.AsyncMock()
        type(mock_tortoise)._inited = mock.PropertyMock(side_effect=[False, True])
        mock_db_cleanup.return_value = mock_count

        # Act
        result = await cleanup_expired_sessions()

        # Assert
        assert result == mock_count
        mock_tortoise.init.assert_awaited_once()
        mock_db_cleanup.assert_awaited_once()
        mock_tortoise.close_connections.assert_awaited_once()
        mock_logger.info.assert_not_called()


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_exception():
    """Test cleanup of expired sessions with an exception."""
    # Arrange
    mock_exception = Exception("Test exception")

    # Mock dependencies
    with (
        mock.patch("backend.tasks.session.Tortoise") as mock_tortoise,
        mock.patch(
            "backend.tasks.session.db_cleanup_expired_sessions"
        ) as mock_db_cleanup,
        mock.patch("backend.tasks.session.logger") as mock_logger,
    ):
        # Configure mocks
        type(mock_tortoise).init = mock.AsyncMock()
        type(mock_tortoise).close_connections = mock.AsyncMock()
        type(mock_tortoise)._inited = mock.PropertyMock(side_effect=[False, True])
        mock_db_cleanup.side_effect = mock_exception

        # Act
        result = await cleanup_expired_sessions()

        # Assert
        assert result == 0
        mock_tortoise.init.assert_awaited_once()
        mock_db_cleanup.assert_awaited_once()
        mock_tortoise.close_connections.assert_awaited_once()
        mock_logger.error.assert_called_once_with(
            f"Error cleaning up expired sessions: {mock_exception}"
        )


@pytest.mark.asyncio
async def test_run_session_cleanup_task():
    """Test the run_session_cleanup_task function."""
    # Arrange
    mock_interval = 0.1  # Short interval for testing

    # Mock dependencies
    with (
        mock.patch("backend.tasks.session.cleanup_expired_sessions") as mock_cleanup,
        mock.patch("backend.tasks.session.asyncio.sleep") as mock_sleep,
    ):
        # Configure mocks
        mock_cleanup.return_value = None
        mock_sleep.side_effect = [None, asyncio.CancelledError()]

        # Act & Assert
        with pytest.raises(asyncio.CancelledError):
            await run_session_cleanup_task(interval_seconds=mock_interval)

        # Verify function calls
        assert mock_cleanup.await_count == 2
        mock_sleep.assert_awaited_with(mock_interval)
