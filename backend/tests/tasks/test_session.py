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
        # Set up Tortoise._inited property mock
        type(mock_tortoise)._inited = mock.PropertyMock(side_effect=[False, True])
        type(mock_tortoise).init = mock.AsyncMock()
        type(mock_tortoise).close_connections = mock.AsyncMock()
        mock_db_cleanup.return_value = mock_count

        # Act
        result = await cleanup_expired_sessions()

        # Assert
        assert result == mock_count
        mock_tortoise.init.assert_awaited_once()
        mock_db_cleanup.assert_awaited_once()
        mock_logger.info.assert_called_once_with(
            f"Cleaned up {mock_count} expired sessions"
        )
        mock_tortoise.close_connections.assert_awaited_once()


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_no_sessions():
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
        type(mock_tortoise)._inited = mock.PropertyMock(side_effect=[False, True])
        type(mock_tortoise).init = mock.AsyncMock()
        type(mock_tortoise).close_connections = mock.AsyncMock()
        mock_db_cleanup.return_value = mock_count

        # Act
        result = await cleanup_expired_sessions()

        # Assert
        assert result == mock_count
        mock_tortoise.init.assert_awaited_once()
        mock_db_cleanup.assert_awaited_once()
        # No logging should occur when count is 0
        mock_logger.info.assert_not_called()
        mock_tortoise.close_connections.assert_awaited_once()


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_already_initialized():
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
        # Configure mocks - Tortoise already initialized
        type(mock_tortoise)._inited = mock.PropertyMock(return_value=True)
        type(mock_tortoise).init = mock.AsyncMock()
        type(mock_tortoise).close_connections = mock.AsyncMock()
        mock_db_cleanup.return_value = mock_count

        # Act
        result = await cleanup_expired_sessions()

        # Assert
        assert result == mock_count
        # Should not initialize if already initialized
        mock_tortoise.init.assert_not_awaited()
        mock_db_cleanup.assert_awaited_once()
        mock_logger.info.assert_called_once_with(
            f"Cleaned up {mock_count} expired sessions"
        )
        mock_tortoise.close_connections.assert_awaited_once()


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_error():
    # Arrange
    mock_error = Exception("Test error")

    # Mock dependencies
    with (
        mock.patch("backend.tasks.session.Tortoise") as mock_tortoise,
        mock.patch(
            "backend.tasks.session.db_cleanup_expired_sessions",
            side_effect=mock_error,
        ) as mock_db_cleanup,
        mock.patch("backend.tasks.session.logger") as mock_logger,
    ):
        # Configure mocks
        type(mock_tortoise)._inited = mock.PropertyMock(side_effect=[False, True])
        type(mock_tortoise).init = mock.AsyncMock()
        type(mock_tortoise).close_connections = mock.AsyncMock()

        # Act
        result = await cleanup_expired_sessions()

        # Assert
        assert result == 0  # Should return 0 on error
        mock_tortoise.init.assert_awaited_once()
        mock_db_cleanup.assert_awaited_once()
        mock_logger.error.assert_called_once_with(
            f"Error cleaning up expired sessions: {mock_error}"
        )
        mock_tortoise.close_connections.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_session_cleanup_task():
    # Arrange
    test_interval = 0.01  # Small interval for testing
    mock_cleanup_calls = 3

    # Mock dependencies
    with (
        mock.patch("backend.tasks.session.cleanup_expired_sessions") as mock_cleanup,
        mock.patch("backend.tasks.session.asyncio.sleep") as mock_sleep,
    ):
        # Configure mocks
        mock_cleanup.return_value = 5

        # Make sleep raise an exception after n calls to break the infinite loop
        call_count = 0

        async def mock_sleep_side_effect(seconds):
            nonlocal call_count
            call_count += 1
            assert seconds == test_interval
            if call_count >= mock_cleanup_calls:
                raise asyncio.CancelledError()

        mock_sleep.side_effect = mock_sleep_side_effect

        # Act & Assert
        with pytest.raises(asyncio.CancelledError):
            await run_session_cleanup_task(interval_seconds=test_interval)

        # Verify the cleanup was called the expected number of times
        assert mock_cleanup.call_count == mock_cleanup_calls
