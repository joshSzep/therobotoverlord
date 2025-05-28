# Standard library imports
from datetime import datetime
from datetime import timedelta
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_event import UserEvent
from backend.db_functions.user_events.count_recent_failed_login_attempts import (
    count_recent_failed_login_attempts,
)


@pytest.mark.asyncio
async def test_count_recent_failed_login_attempts_with_failures() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_hours = 24
    expected_count = 3

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.count_recent_failed_login_attempts.now_utc",
            return_value=datetime.now(),
        ) as mock_now_utc,
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.count = mock.AsyncMock(return_value=expected_count)

        # Act
        result = await count_recent_failed_login_attempts(
            user_id=test_user_id,
            hours=test_hours,
        )

        # Assert
        assert result == expected_count

        # Verify function calls
        time_threshold = mock_now_utc.return_value - timedelta(hours=test_hours)
        mock_filter.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
            created_at__gte=time_threshold,
        )
        mock_query.filter.assert_called_once_with(metadata__contains={"success": False})
        mock_query.count.assert_called_once()


@pytest.mark.asyncio
async def test_count_recent_failed_login_attempts_no_failures() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_hours = 24
    expected_count = 0

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.count_recent_failed_login_attempts.now_utc",
            return_value=datetime.now(),
        ) as mock_now_utc,
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.count = mock.AsyncMock(return_value=expected_count)

        # Act
        result = await count_recent_failed_login_attempts(
            user_id=test_user_id,
            hours=test_hours,
        )

        # Assert
        assert result == expected_count

        # Verify function calls
        time_threshold = mock_now_utc.return_value - timedelta(hours=test_hours)
        mock_filter.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
            created_at__gte=time_threshold,
        )
        mock_query.filter.assert_called_once_with(metadata__contains={"success": False})
        mock_query.count.assert_called_once()


@pytest.mark.asyncio
async def test_count_recent_failed_login_attempts_custom_time_window() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_hours = 12  # Custom time window
    expected_count = 2

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.count_recent_failed_login_attempts.now_utc",
            return_value=datetime.now(),
        ) as mock_now_utc,
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.count = mock.AsyncMock(return_value=expected_count)

        # Act
        result = await count_recent_failed_login_attempts(
            user_id=test_user_id,
            hours=test_hours,
        )

        # Assert
        assert result == expected_count

        # Verify function calls
        time_threshold = mock_now_utc.return_value - timedelta(hours=test_hours)
        mock_filter.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
            created_at__gte=time_threshold,
        )
        mock_query.filter.assert_called_once_with(metadata__contains={"success": False})
        mock_query.count.assert_called_once()


@pytest.mark.asyncio
async def test_count_recent_failed_login_attempts_db_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    db_error = OperationalError("Database error")

    # Mock the now_utc function
    with (
        mock.patch(
            "backend.db_functions.user_events.count_recent_failed_login_attempts.now_utc",
            return_value=datetime.now(),
        ),
        # Mock the filter method to raise an error
        mock.patch.object(UserEvent, "filter", side_effect=db_error) as mock_filter,
    ):
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await count_recent_failed_login_attempts(user_id=test_user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        assert mock_filter.called


@pytest.mark.asyncio
async def test_count_recent_failed_login_attempts_query_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    query_error = OperationalError("Query error")

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.count_recent_failed_login_attempts.now_utc",
            return_value=datetime.now(),
        ),
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.count = mock.AsyncMock(side_effect=query_error)

        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await count_recent_failed_login_attempts(user_id=test_user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == query_error
        assert mock_filter.called
        assert mock_query.filter.called
        assert mock_query.count.called
