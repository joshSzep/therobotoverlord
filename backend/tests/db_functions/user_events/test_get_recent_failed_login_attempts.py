# Standard library imports
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import List
from unittest import mock
from uuid import uuid4

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_event import UserEvent
from backend.db_functions.user_events.get_recent_failed_login_attempts import (
    get_recent_failed_login_attempts,
)
from backend.schemas.user_event import UserEventSchema


@pytest.fixture
def mock_login_events() -> List[mock.MagicMock]:
    events = []
    user_id = uuid4()

    for i in range(5):
        event = mock.MagicMock(spec=UserEvent)
        event.id = uuid4()
        event.user_id = user_id
        event.event_type = "login"
        event.ip_address = f"192.168.1.{i}"
        # All events are failed login attempts
        event.metadata = {"success": False}
        event.created_at = mock.MagicMock()
        event.updated_at = mock.MagicMock()
        events.append(event)

    return events


@pytest.fixture
def mock_event_schemas(mock_login_events) -> List[UserEventSchema]:
    return [
        UserEventSchema(
            id=event.id,
            user_id=event.user_id,
            event_type=event.event_type,
            ip_address=event.ip_address,
            metadata=event.metadata,
            created_at=datetime(2025, 5, 28, tzinfo=UTC),
            updated_at=datetime(2025, 5, 28, tzinfo=UTC),
        )
        for event in mock_login_events
    ]


@pytest.mark.asyncio
async def test_get_recent_failed_login_attempts_success(
    mock_login_events, mock_event_schemas
) -> None:
    # Arrange
    test_user_id = mock_login_events[0].user_id
    test_hours = 24
    test_limit = 3

    # Mock the database query and now_utc function
    with (
        mock.patch(
            "backend.db_functions.user_events.get_recent_failed_login_attempts.now_utc"
        ) as mock_now,
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.get_recent_failed_login_attempts.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_event_schemas[:test_limit]),
        ),
    ):
        # Configure mocks
        mock_now.return_value = datetime(2025, 5, 28, tzinfo=UTC)
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.AsyncMock(return_value=mock_login_events[:test_limit])

        # Act
        result = await get_recent_failed_login_attempts(
            user_id=test_user_id,
            hours=test_hours,
            limit=test_limit,
        )

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == test_limit

        # Verify function calls
        time_threshold = mock_now.return_value - timedelta(hours=test_hours)
        mock_filter.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
            created_at__gte=time_threshold,
        )
        mock_query.filter.assert_called_once_with(metadata__contains={"success": False})
        mock_query.order_by.assert_called_once_with("-created_at")
        mock_query.limit.assert_awaited_once_with(test_limit)

        # Verify schema objects are returned (RULE #5)
        for event_schema in result:
            assert isinstance(event_schema, UserEventSchema)


@pytest.mark.asyncio
async def test_get_recent_failed_login_attempts_with_default_params() -> None:
    # Arrange
    test_user_id = uuid4()
    default_hours = 24
    default_limit = 10
    mock_events = [mock.MagicMock(spec=UserEvent) for _ in range(default_limit)]
    mock_schemas = [mock.MagicMock(spec=UserEventSchema) for _ in range(default_limit)]

    # Mock the database query and now_utc function
    with (
        mock.patch(
            "backend.db_functions.user_events.get_recent_failed_login_attempts.now_utc"
        ) as mock_now,
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.get_recent_failed_login_attempts.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_schemas),
        ),
    ):
        # Configure mocks
        mock_now.return_value = datetime(2025, 5, 28, tzinfo=UTC)
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.AsyncMock(return_value=mock_events)

        # Act
        result = await get_recent_failed_login_attempts(user_id=test_user_id)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == default_limit

        # Verify function calls
        time_threshold = mock_now.return_value - timedelta(hours=default_hours)
        mock_filter.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
            created_at__gte=time_threshold,
        )
        mock_query.filter.assert_called_once_with(metadata__contains={"success": False})
        mock_query.order_by.assert_called_once_with("-created_at")
        mock_query.limit.assert_awaited_once_with(default_limit)


@pytest.mark.asyncio
async def test_get_recent_failed_login_attempts_no_events() -> None:
    # Arrange
    test_user_id = uuid4()
    test_hours = 24
    test_limit = 10

    # Mock the database query and now_utc function
    with (
        mock.patch(
            "backend.db_functions.user_events.get_recent_failed_login_attempts.now_utc"
        ) as mock_now,
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
    ):
        # Configure mocks
        mock_now.return_value = datetime(2025, 5, 28, tzinfo=UTC)
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.AsyncMock(return_value=[])  # No events returned

        # Act
        result = await get_recent_failed_login_attempts(
            user_id=test_user_id,
            hours=test_hours,
            limit=test_limit,
        )

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

        # Verify function calls
        time_threshold = mock_now.return_value - timedelta(hours=test_hours)
        mock_filter.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
            created_at__gte=time_threshold,
        )
        mock_query.filter.assert_called_once_with(metadata__contains={"success": False})
        mock_query.order_by.assert_called_once_with("-created_at")
        mock_query.limit.assert_awaited_once_with(test_limit)


@pytest.mark.asyncio
async def test_get_recent_failed_login_attempts_db_error() -> None:
    # Arrange
    test_user_id = uuid4()
    db_error = OperationalError("Database error")

    # Mock the database query to raise an error
    with (
        mock.patch(
            "backend.db_functions.user_events.get_recent_failed_login_attempts.now_utc"
        ),
        mock.patch.object(UserEvent, "filter", side_effect=db_error) as mock_filter,
    ):
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await get_recent_failed_login_attempts(user_id=test_user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once()
