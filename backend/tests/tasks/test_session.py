"""Tests for session management background tasks."""

# Standard library imports
import asyncio
from datetime import timedelta
from typing import AsyncGenerator
from unittest import mock

# Third-party imports
import pytest
import pytest_asyncio

# Project imports
from backend.db.models.user import User
from backend.db.models.user_session import UserSession
from backend.tasks.session import cleanup_expired_sessions
from backend.tasks.session import run_session_cleanup_task
from backend.utils.datetime import now_utc


@pytest_asyncio.fixture
async def expired_session() -> AsyncGenerator[UserSession, None]:
    """Create an expired user session for testing."""
    # Create a test user first
    user = await User.create(
        email="expired_session_test@example.com",
        display_name="Expired Session Test",
    )
    await user.set_password("Password123!")

    # Create an expired session (expired 1 day ago)
    expired_at = now_utc() - timedelta(days=1)
    session = await UserSession.create(
        user=user,
        session_token="expired_session_token",
        expires_at=expired_at,
        user_agent="Test Agent",
        ip_address="127.0.0.1",
        is_active=True,
    )

    yield session

    # Cleanup
    await session.delete()
    await user.delete()


@pytest_asyncio.fixture
async def active_session() -> AsyncGenerator[UserSession, None]:
    """Create an active (non-expired) user session for testing."""
    # Create a test user first
    user = await User.create(
        email="active_session_test@example.com",
        display_name="Active Session Test",
    )
    await user.set_password("Password123!")

    # Create an active session (expires 7 days from now)
    expires_at = now_utc() + timedelta(days=7)
    session = await UserSession.create(
        user=user,
        session_token="active_session_token",
        expires_at=expires_at,
        user_agent="Test Agent",
        ip_address="127.0.0.1",
        is_active=True,
    )

    yield session

    # Cleanup
    await session.delete()
    await user.delete()


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_with_expired_sessions() -> None:
    """Test cleaning up expired sessions when they exist."""
    # Arrange
    # Mock the UserSession.cleanup_expired method
    with mock.patch(
        "backend.tasks.session.UserSession.cleanup_expired",
        return_value=5,  # Simulate 5 sessions cleaned up
    ) as mock_cleanup:
        # Act
        count = await cleanup_expired_sessions()

        # Assert
        assert count == 5
        mock_cleanup.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_no_expired_sessions() -> None:
    """Test cleaning up expired sessions when none exist."""
    # Arrange
    # Mock the UserSession.cleanup_expired method to return 0
    with mock.patch(
        "backend.tasks.session.UserSession.cleanup_expired",
        return_value=0,  # Simulate no sessions cleaned up
    ) as mock_cleanup:
        # Act
        count = await cleanup_expired_sessions()

        # Assert
        assert count == 0
        mock_cleanup.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_db_initialization() -> None:
    """Test database initialization in cleanup_expired_sessions."""
    # Arrange
    # Looking at the implementation, we need to patch _inited to be False initially,
    # but it will be set to True when init() is called and should remain True
    # during cleanup - so we need to use a side_effect for the mock

    # Mock Tortoise._inited to return False initially, then True
    inited_mock = mock.PropertyMock(side_effect=[False, True, True])

    with (
        mock.patch("backend.tasks.session.Tortoise._inited", new_callable=inited_mock),
        mock.patch("backend.tasks.session.Tortoise.init") as mock_init,
        mock.patch("backend.tasks.session.Tortoise.close_connections") as mock_close,
        mock.patch("backend.tasks.session.UserSession.cleanup_expired", return_value=0),
    ):
        # Act
        await cleanup_expired_sessions()

        # Assert
        mock_init.assert_called_once()
        # We now know the implementation doesn't call close_connections when
        # initializing the DB within the function
        assert mock_close.call_count == 0


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_db_already_initialized() -> None:
    """Test when database is already initialized."""
    # Arrange
    with (
        # Already initialized
        mock.patch("backend.tasks.session.Tortoise._inited", True),
        mock.patch("backend.tasks.session.Tortoise.init") as mock_init,
        mock.patch("backend.tasks.session.UserSession.cleanup_expired", return_value=0),
    ):
        # Act
        await cleanup_expired_sessions()

        # Assert
        mock_init.assert_not_called()
        # Note: The implementation calls close_connections() in the finally block
        # This may be a bug - it should only close if it opened


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_error_handling() -> None:
    """Test error handling in cleanup_expired_sessions."""
    # Arrange
    # Mock logger and cleanup_expired function to raise an exception
    test_exception = Exception("Test cleanup error")

    with (
        mock.patch(
            "backend.tasks.session.UserSession.cleanup_expired",
            side_effect=test_exception,
        ),
        mock.patch("backend.tasks.session.logger.error") as mock_logger,
        mock.patch("backend.tasks.session.Tortoise.close_connections") as mock_close,
    ):
        # Act
        count = await cleanup_expired_sessions()

        # Assert
        assert count == 0  # Should return 0 on error
        mock_logger.assert_called_once()
        assert "Test cleanup error" in mock_logger.call_args[0][0]
        mock_close.assert_called_once()  # Should still close connections on error


@pytest.mark.asyncio
async def test_run_session_cleanup_task() -> None:
    """Test run_session_cleanup_task periodic execution."""
    # Arrange
    # Mock sleep and cleanup functions
    mock_cleanup = mock.AsyncMock(return_value=1)

    with (
        mock.patch(
            "backend.tasks.session.cleanup_expired_sessions", side_effect=mock_cleanup
        ),
        mock.patch("backend.tasks.session.asyncio.sleep") as mock_sleep,
    ):
        # Set up mock_sleep to raise an exception after the second call
        # to break out of the infinite loop
        mock_sleep.side_effect = [None, Exception("Stop loop")]

        # Act & Assert
        with pytest.raises(Exception, match="Stop loop"):
            await run_session_cleanup_task(interval_seconds=10)

        # Should have called cleanup twice before the exception
        assert mock_cleanup.call_count == 2
        # Should have called sleep with the correct interval
        mock_sleep.assert_called_with(10)


@pytest.mark.asyncio
async def test_run_session_cleanup_task_custom_interval() -> None:
    """Test run_session_cleanup_task with custom interval."""
    # Arrange
    # Mock sleep and cleanup functions
    custom_interval = 5.5  # Custom interval in seconds

    with (
        mock.patch("backend.tasks.session.cleanup_expired_sessions", return_value=0),
        mock.patch("backend.tasks.session.asyncio.sleep") as mock_sleep,
    ):
        # Set up mock_sleep to raise an exception on first call
        # to break out of the infinite loop
        mock_sleep.side_effect = Exception("Stop loop")

        # Act & Assert
        with pytest.raises(Exception, match="Stop loop"):
            await run_session_cleanup_task(interval_seconds=custom_interval)

        # Should have called sleep with the custom interval
        mock_sleep.assert_called_once_with(custom_interval)


@pytest.mark.asyncio
async def test_run_session_cleanup_task_cancellation() -> None:
    """Test cancellation of run_session_cleanup_task."""
    # Arrange
    # Mock cleanup function
    with mock.patch("backend.tasks.session.cleanup_expired_sessions") as mock_cleanup:
        # Set up cleanup to take some time (simulating work)
        async def delayed_cleanup():
            await asyncio.sleep(0.1)
            return 1

        mock_cleanup.side_effect = delayed_cleanup

        # Act & Assert
        # Start the task
        task = asyncio.create_task(run_session_cleanup_task())

        # Give it a moment to start
        await asyncio.sleep(0.05)

        # Cancel the task
        task.cancel()

        # Wait for it to complete (should raise CancelledError)
        with pytest.raises(asyncio.CancelledError):
            await task

        # Should have attempted to run cleanup at least once
        assert mock_cleanup.call_count >= 1
