# Standard library imports
from datetime import UTC
from datetime import datetime
from typing import List
from unittest import mock
from uuid import uuid4

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_event import UserEvent
from backend.db_functions.user_events.list_login_attempts import list_login_attempts
from backend.schemas.user_event import UserEventListSchema
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
        # Alternate between success and failure
        event.metadata = {"success": i % 2 == 0}
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
async def test_list_login_attempts_no_filters(
    mock_login_events, mock_event_schemas
) -> None:
    # Arrange
    total_count = len(mock_login_events)

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.list_login_attempts.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_event_schemas),
        ),
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.count = mock.AsyncMock(return_value=total_count)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=mock_login_events)

        # Act
        result = await list_login_attempts()

        # Assert
        assert result is not None
        assert isinstance(result, UserEventListSchema)
        assert result.count == total_count
        assert len(result.user_events) == total_count

        # Verify function calls
        mock_filter.assert_called_once_with(event_type="login")
        mock_query.count.assert_awaited_once()
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(20)
        mock_query.order_by.assert_awaited_once_with("-created_at")

        # No need to verify converter calls since we're mocking at the module level

        # Verify schema objects are returned (RULE #5)
        for event_schema in result.user_events:
            assert isinstance(event_schema, UserEventSchema)


@pytest.mark.asyncio
async def test_list_login_attempts_with_user_id(
    mock_login_events, mock_event_schemas
) -> None:
    # Arrange
    test_user_id = uuid4()
    total_count = len(mock_login_events)

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.list_login_attempts.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_event_schemas),
        ),
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.count = mock.AsyncMock(return_value=total_count)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=mock_login_events)

        # Act
        result = await list_login_attempts(user_id=test_user_id)

        # Assert
        assert result is not None
        assert isinstance(result, UserEventListSchema)
        assert result.count == total_count
        assert len(result.user_events) == total_count

        # Verify function calls
        mock_filter.assert_called_once_with(event_type="login")
        mock_query.filter.assert_called_once_with(user_id=test_user_id)
        mock_query.count.assert_awaited_once()
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(20)
        mock_query.order_by.assert_awaited_once_with("-created_at")

        # No need to verify converter calls since we're mocking at the module level


@pytest.mark.asyncio
async def test_list_login_attempts_with_ip_address(
    mock_login_events, mock_event_schemas
) -> None:
    # Arrange
    test_ip = "192.168.1.1"
    total_count = len(mock_login_events)

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.list_login_attempts.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_event_schemas),
        ),
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.count = mock.AsyncMock(return_value=total_count)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=mock_login_events)

        # Act
        result = await list_login_attempts(ip_address=test_ip)

        # Assert
        assert result is not None
        assert isinstance(result, UserEventListSchema)
        assert result.count == total_count
        assert len(result.user_events) == total_count

        # Verify function calls
        mock_filter.assert_called_once_with(event_type="login")
        mock_query.filter.assert_called_once_with(ip_address=test_ip)
        mock_query.count.assert_awaited_once()
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(20)
        mock_query.order_by.assert_awaited_once_with("-created_at")


@pytest.mark.asyncio
async def test_list_login_attempts_with_success(
    mock_login_events, mock_event_schemas
) -> None:
    # Arrange
    test_success = True
    total_count = len(mock_login_events)

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.list_login_attempts.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_event_schemas),
        ),
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.count = mock.AsyncMock(return_value=total_count)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=mock_login_events)

        # Act
        result = await list_login_attempts(success=test_success)

        # Assert
        assert result is not None
        assert isinstance(result, UserEventListSchema)
        assert result.count == total_count
        assert len(result.user_events) == total_count

        # Verify function calls
        mock_filter.assert_called_once_with(event_type="login")
        mock_query.filter.assert_called_once_with(
            metadata__contains={"success": test_success}
        )
        mock_query.count.assert_awaited_once()
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(20)
        mock_query.order_by.assert_awaited_once_with("-created_at")


@pytest.mark.asyncio
async def test_list_login_attempts_with_pagination(
    mock_login_events, mock_event_schemas
) -> None:
    # Arrange
    test_skip = 2
    test_limit = 3
    total_count = 10  # Total in database

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.list_login_attempts.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_event_schemas),
        ),
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.count = mock.AsyncMock(return_value=total_count)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=mock_login_events)

        # Act
        result = await list_login_attempts(skip=test_skip, limit=test_limit)

        # Assert
        assert result is not None
        assert isinstance(result, UserEventListSchema)
        assert result.count == total_count
        assert len(result.user_events) == len(mock_login_events)

        # Verify function calls
        mock_filter.assert_called_once_with(event_type="login")
        mock_query.count.assert_awaited_once()
        mock_query.offset.assert_called_once_with(test_skip)
        mock_query.limit.assert_called_once_with(test_limit)
        mock_query.order_by.assert_awaited_once_with("-created_at")


@pytest.mark.asyncio
async def test_list_login_attempts_with_all_filters(
    mock_login_events, mock_event_schemas
) -> None:
    # Arrange
    test_user_id = uuid4()
    test_ip = "192.168.1.1"
    test_success = True
    test_skip = 2
    test_limit = 3
    total_count = len(mock_login_events)

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.list_login_attempts.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_event_schemas),
        ),
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.count = mock.AsyncMock(return_value=total_count)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=mock_login_events)

        # Act
        result = await list_login_attempts(
            user_id=test_user_id,
            ip_address=test_ip,
            success=test_success,
            skip=test_skip,
            limit=test_limit,
        )

        # Assert
        assert result is not None
        assert isinstance(result, UserEventListSchema)
        assert result.count == total_count
        assert len(result.user_events) == len(mock_login_events)

        # Verify function calls
        mock_filter.assert_called_once_with(event_type="login")

        # Verify all filters were applied
        assert mock_query.filter.call_count == 3
        mock_query.filter.assert_any_call(user_id=test_user_id)
        mock_query.filter.assert_any_call(ip_address=test_ip)
        mock_query.filter.assert_any_call(metadata__contains={"success": test_success})

        mock_query.count.assert_awaited_once()
        mock_query.offset.assert_called_once_with(test_skip)
        mock_query.limit.assert_called_once_with(test_limit)
        mock_query.order_by.assert_awaited_once_with("-created_at")


@pytest.mark.asyncio
async def test_list_login_attempts_db_error() -> None:
    # Arrange
    db_error = OperationalError("Database error")

    # Mock the filter method to raise an error
    with mock.patch.object(UserEvent, "filter", side_effect=db_error) as mock_filter:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await list_login_attempts()

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(event_type="login")
