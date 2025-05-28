# Standard library imports
from typing import List
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_event import UserEvent
from backend.db_functions.user_events.get_recent_login_attempts import (
    get_recent_login_attempts,
)
from backend.schemas.user_event import UserEventSchema


@pytest.fixture
def mock_login_events() -> List[mock.MagicMock]:
    events = []
    user_id = uuid.uuid4()

    for i in range(5):
        event = mock.MagicMock(spec=UserEvent)
        event.id = uuid.uuid4()
        event.user_id = user_id
        event.event_type = "login"
        event.ip_address = f"192.168.1.{i}"
        event.user_agent = f"Mozilla/5.0 Test Browser {i}"
        # Alternate between success and failure
        event.metadata = {"success": i % 2 == 0}
        event.created_at = mock.MagicMock()
        event.updated_at = mock.MagicMock()
        event.fetch_related = mock.AsyncMock()
        event.user = mock.MagicMock()
        event.user.id = user_id
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
            user_agent=event.user_agent,
            metadata=event.metadata,
            created_at=event.created_at,
            updated_at=event.updated_at,
        )
        for event in mock_login_events
    ]


@pytest.mark.asyncio
async def test_get_recent_login_attempts_success(
    mock_login_events, mock_event_schemas
) -> None:
    # Arrange
    test_user_id = mock_login_events[0].user_id
    test_limit = 3

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.get_recent_login_attempts.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_event_schemas[:test_limit]),
        ) as mock_converter,
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.order_by = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.AsyncMock(return_value=mock_login_events[:test_limit])

        # Act
        result = await get_recent_login_attempts(
            user_id=test_user_id,
            limit=test_limit,
        )

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == test_limit

        # Verify function calls
        mock_filter.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
        )
        mock_query.order_by.assert_called_once_with("-created_at")
        mock_query.limit.assert_called_once_with(test_limit)

        # Verify converter was called for each event
        assert mock_converter.call_count == test_limit
        for i in range(test_limit):
            mock_converter.assert_any_call(mock_login_events[i])

        # Verify schema objects are returned (RULE #5)
        for event_schema in result:
            assert isinstance(event_schema, UserEventSchema)


@pytest.mark.asyncio
async def test_get_recent_login_attempts_with_default_limit() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    default_limit = 10
    mock_events = [mock.MagicMock(spec=UserEvent) for _ in range(default_limit)]
    mock_schemas = [mock.MagicMock(spec=UserEventSchema) for _ in range(default_limit)]

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.get_recent_login_attempts.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_schemas),
        ),
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.order_by = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.AsyncMock(return_value=mock_events)

        # Act
        result = await get_recent_login_attempts(user_id=test_user_id)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == default_limit

        # Verify function calls
        mock_filter.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
        )
        mock_query.order_by.assert_called_once_with("-created_at")
        mock_query.limit.assert_called_once_with(default_limit)


@pytest.mark.asyncio
async def test_get_recent_login_attempts_no_events() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_limit = 10

    # Mock the database query
    with mock.patch.object(
        UserEvent, "filter", return_value=mock.MagicMock()
    ) as mock_filter:
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.order_by = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.AsyncMock(return_value=[])

        # Act
        result = await get_recent_login_attempts(
            user_id=test_user_id,
            limit=test_limit,
        )

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

        # Verify function calls
        mock_filter.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
        )
        mock_query.order_by.assert_called_once_with("-created_at")
        mock_query.limit.assert_called_once_with(test_limit)


@pytest.mark.asyncio
async def test_get_recent_login_attempts_db_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    db_error = OperationalError("Database error")

    # Mock the filter method to raise an error
    with mock.patch.object(UserEvent, "filter", side_effect=db_error) as mock_filter:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await get_recent_login_attempts(user_id=test_user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
        )
