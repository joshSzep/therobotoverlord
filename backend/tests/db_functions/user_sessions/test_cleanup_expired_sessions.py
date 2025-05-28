# Standard library imports
from datetime import datetime
from unittest import mock

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_session import UserSession
from backend.db_functions.user_sessions.cleanup_expired_sessions import (
    cleanup_expired_sessions,
)


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_success() -> None:
    # Arrange
    test_count = 5
    test_now = datetime.now()

    # Mock the filter and update methods
    filter_mock = mock.AsyncMock()
    filter_mock.update = mock.AsyncMock(return_value=test_count)

    with (
        mock.patch.object(
            UserSession, "filter", return_value=filter_mock
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_sessions.cleanup_expired_sessions.now_utc",
            return_value=test_now,
        ) as mock_now_utc,
    ):
        # Act
        result = await cleanup_expired_sessions()

        # Assert
        assert result == test_count
        mock_filter.assert_called_once_with(
            expires_at__lt=test_now,
            is_active=True,
        )
        filter_mock.update.assert_called_once_with(is_active=False)
        mock_now_utc.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_no_expired() -> None:
    # Arrange
    test_count = 0
    test_now = datetime.now()

    # Mock the filter and update methods
    filter_mock = mock.AsyncMock()
    filter_mock.update = mock.AsyncMock(return_value=test_count)

    with (
        mock.patch.object(
            UserSession, "filter", return_value=filter_mock
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_sessions.cleanup_expired_sessions.now_utc",
            return_value=test_now,
        ) as mock_now_utc,
    ):
        # Act
        result = await cleanup_expired_sessions()

        # Assert
        assert result == 0
        mock_filter.assert_called_once_with(
            expires_at__lt=test_now,
            is_active=True,
        )
        filter_mock.update.assert_called_once_with(is_active=False)
        mock_now_utc.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_filter_error() -> None:
    # Arrange
    db_error = OperationalError("Database error")
    test_now = datetime.now()

    # Mock the filter method to raise an error
    with (
        mock.patch.object(UserSession, "filter", side_effect=db_error) as mock_filter,
        mock.patch(
            "backend.db_functions.user_sessions.cleanup_expired_sessions.now_utc",
            return_value=test_now,
        ) as mock_now_utc,
    ):
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await cleanup_expired_sessions()

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(
            expires_at__lt=test_now,
            is_active=True,
        )
        mock_now_utc.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_update_error() -> None:
    # Arrange
    db_error = OperationalError("Update error")
    test_now = datetime.now()

    # Mock the filter and update methods
    filter_mock = mock.AsyncMock()
    filter_mock.update = mock.AsyncMock(side_effect=db_error)

    with (
        mock.patch.object(
            UserSession, "filter", return_value=filter_mock
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_sessions.cleanup_expired_sessions.now_utc",
            return_value=test_now,
        ) as mock_now_utc,
    ):
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await cleanup_expired_sessions()

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(
            expires_at__lt=test_now,
            is_active=True,
        )
        filter_mock.update.assert_called_once_with(is_active=False)
        mock_now_utc.assert_called_once()
