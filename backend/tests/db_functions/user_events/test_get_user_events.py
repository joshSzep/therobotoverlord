# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_event import UserEvent
from backend.db_functions.user_events.get_user_events import get_user_events
from backend.schemas.user_event import UserEventListSchema
from backend.schemas.user_event import UserEventSchema


@pytest.fixture
def mock_user_events() -> list[mock.MagicMock]:
    events = []
    for i in range(3):
        event = mock.MagicMock(spec=UserEvent)
        event.id = uuid.uuid4()
        event.user_id = uuid.uuid4()
        event.event_type = ["login", "logout", "password_change"][i]
        event.ip_address = f"192.168.1.{i}"
        event.user_agent = "Mozilla/5.0"
        event.metadata = {"key": f"value{i}"} if i % 2 == 0 else None
        event.created_at = mock.MagicMock()
        event.updated_at = mock.MagicMock()
        event.fetch_related = mock.AsyncMock()
        event.user = mock.MagicMock()
        event.user.id = event.user_id
        events.append(event)
    return events


@pytest.fixture
def mock_event_schemas(mock_user_events) -> list[UserEventSchema]:
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
        for event in mock_user_events
    ]


@pytest.mark.asyncio
async def test_get_user_events_success(mock_user_events, mock_event_schemas) -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_skip = 0
    test_limit = 20
    test_count = len(mock_user_events)

    # Mock the database query - RULE #10 compliance: only operates on UserEvent model
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.get_user_events.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_event_schemas),
        ) as mock_converter,
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.count = mock.AsyncMock(return_value=test_count)
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=mock_user_events)

        # Act
        result = await get_user_events(
            user_id=test_user_id,
            skip=test_skip,
            limit=test_limit,
        )

        # Assert
        assert result is not None
        assert isinstance(result, UserEventListSchema)
        assert len(result.user_events) == len(mock_user_events)
        assert result.count == test_count

        # Verify function calls
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.count.assert_called_once()
        mock_query.offset.assert_called_once_with(test_skip)
        mock_query.limit.assert_called_once_with(test_limit)
        mock_query.order_by.assert_called_once_with("-created_at")

        # Verify converter was called for each event
        assert mock_converter.call_count == len(mock_user_events)
        for i, event in enumerate(mock_user_events):
            mock_converter.assert_any_call(event)

        # Verify schema objects are returned (RULE #5)
        for event_schema in result.user_events:
            assert isinstance(event_schema, UserEventSchema)


@pytest.mark.asyncio
async def test_get_user_events_with_event_type(
    mock_user_events, mock_event_schemas
) -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_skip = 0
    test_limit = 20
    test_event_type = "login"
    test_count = 1
    filtered_events = [mock_user_events[0]]  # Just the login event

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.get_user_events.user_event_to_schema",
            new=mock.AsyncMock(return_value=mock_event_schemas[0]),
        ) as mock_converter,
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.count = mock.AsyncMock(return_value=test_count)
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=filtered_events)

        # Act
        result = await get_user_events(
            user_id=test_user_id,
            skip=test_skip,
            limit=test_limit,
            event_type=test_event_type,
        )

        # Assert
        assert result is not None
        assert isinstance(result, UserEventListSchema)
        assert len(result.user_events) == len(filtered_events)
        assert result.count == test_count

        # Verify function calls
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.filter.assert_called_once_with(event_type=test_event_type)
        mock_query.count.assert_called_once()
        mock_query.offset.assert_called_once_with(test_skip)
        mock_query.limit.assert_called_once_with(test_limit)
        mock_query.order_by.assert_called_once_with("-created_at")

        # Verify converter was called for each event
        assert mock_converter.call_count == len(filtered_events)


@pytest.mark.asyncio
async def test_get_user_events_empty() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_skip = 0
    test_limit = 20
    test_count = 0

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.count = mock.AsyncMock(return_value=test_count)
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=[])

        # Act
        result = await get_user_events(
            user_id=test_user_id,
            skip=test_skip,
            limit=test_limit,
        )

        # Assert
        assert result is not None
        assert isinstance(result, UserEventListSchema)
        assert len(result.user_events) == 0
        assert result.count == 0

        # Verify function calls
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.count.assert_called_once()
        mock_query.offset.assert_called_once_with(test_skip)
        mock_query.limit.assert_called_once_with(test_limit)
        mock_query.order_by.assert_called_once_with("-created_at")


@pytest.mark.asyncio
async def test_get_user_events_with_pagination() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_skip = 5
    test_limit = 10
    test_count = 25
    mock_page_events = [mock.MagicMock(spec=UserEvent) for _ in range(10)]
    for event in mock_page_events:
        event.fetch_related = mock.AsyncMock()

    mock_schemas = [
        mock.MagicMock(spec=UserEventSchema) for _ in range(len(mock_page_events))
    ]

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.get_user_events.user_event_to_schema",
            new=mock.AsyncMock(side_effect=mock_schemas),
        ) as mock_converter,
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.count = mock.AsyncMock(return_value=test_count)
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=mock_page_events)

        # Act
        result = await get_user_events(
            user_id=test_user_id,
            skip=test_skip,
            limit=test_limit,
        )

        # Assert
        assert result is not None
        assert isinstance(result, UserEventListSchema)
        assert len(result.user_events) == len(mock_page_events)
        assert result.count == test_count

        # Verify function calls
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.count.assert_called_once()
        mock_query.offset.assert_called_once_with(test_skip)
        mock_query.limit.assert_called_once_with(test_limit)
        mock_query.order_by.assert_called_once_with("-created_at")

        # Verify converter was called for each event
        assert mock_converter.call_count == len(mock_page_events)


@pytest.mark.asyncio
async def test_get_user_events_database_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_skip = 0
    test_limit = 20
    db_error = OperationalError("Database error")

    # Mock the database query
    with mock.patch.object(
        UserEvent, "filter", return_value=mock.MagicMock()
    ) as mock_filter:
        # Mock the query method to raise an error
        mock_query = mock_filter.return_value
        mock_query.count = mock.AsyncMock(side_effect=db_error)

        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await get_user_events(
                user_id=test_user_id,
                skip=test_skip,
                limit=test_limit,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.count.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_events_query_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_skip = 0
    test_limit = 20
    test_count = 10
    db_error = OperationalError("Query error")

    # Mock the database query
    with mock.patch.object(
        UserEvent, "filter", return_value=mock.MagicMock()
    ) as mock_filter:
        # Mock the count method to succeed but the query to fail
        mock_query = mock_filter.return_value
        mock_query.count = mock.AsyncMock(return_value=test_count)
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(side_effect=db_error)

        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await get_user_events(
                user_id=test_user_id,
                skip=test_skip,
                limit=test_limit,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.count.assert_called_once()
        mock_query.offset.assert_called_once_with(test_skip)
        mock_query.limit.assert_called_once_with(test_limit)
        mock_query.order_by.assert_called_once_with("-created_at")


@pytest.mark.asyncio
async def test_get_user_events_converter_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_skip = 0
    test_limit = 20
    test_count = 3
    mock_events = [mock.MagicMock(spec=UserEvent) for _ in range(3)]
    for event in mock_events:
        event.fetch_related = mock.AsyncMock()
    converter_error = ValueError("Converter error")

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_events.get_user_events.user_event_to_schema",
            new=mock.AsyncMock(side_effect=converter_error),
        ) as mock_converter,
    ):
        # Mock the query methods
        mock_query = mock_filter.return_value
        mock_query.count = mock.AsyncMock(return_value=test_count)
        mock_query.filter = mock.MagicMock(return_value=mock_query)
        mock_query.offset = mock.MagicMock(return_value=mock_query)
        mock_query.limit = mock.MagicMock(return_value=mock_query)
        mock_query.order_by = mock.AsyncMock(return_value=mock_events)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await get_user_events(
                user_id=test_user_id,
                skip=test_skip,
                limit=test_limit,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == converter_error
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.count.assert_called_once()
        mock_query.offset.assert_called_once_with(test_skip)
        mock_query.limit.assert_called_once_with(test_limit)
        mock_query.order_by.assert_called_once_with("-created_at")
        mock_converter.assert_called_once_with(mock_events[0])
