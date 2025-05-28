# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.user_event import UserEvent
from backend.db_functions.user_events.create_event import create_event
from backend.schemas.user_event import UserEventSchema


@pytest.fixture
def mock_user_event() -> mock.MagicMock:
    event = mock.MagicMock(spec=UserEvent)
    event.id = uuid.uuid4()
    event.user_id = uuid.uuid4()
    event.event_type = "login_success"
    event.ip_address = "192.168.1.1"
    event.user_agent = "Mozilla/5.0"
    event.resource_type = "user"
    event.resource_id = uuid.uuid4()
    event.metadata = {"key": "value"}
    event.created_at = mock.MagicMock()
    event.updated_at = mock.MagicMock()
    # Add fetch_related method for the converter
    event.fetch_related = mock.AsyncMock()
    # Mock the user property
    event.user = mock.MagicMock()
    event.user.id = event.user_id
    return event


@pytest.fixture
def mock_event_schema(mock_user_event) -> UserEventSchema:
    return UserEventSchema(
        id=mock_user_event.id,
        user_id=mock_user_event.user_id,
        event_type=mock_user_event.event_type,
        ip_address=mock_user_event.ip_address,
        user_agent=mock_user_event.user_agent,
        resource_type=mock_user_event.resource_type,
        resource_id=mock_user_event.resource_id,
        metadata=mock_user_event.metadata,
        created_at=mock_user_event.created_at,
        updated_at=mock_user_event.updated_at,
    )


@pytest.mark.asyncio
async def test_create_event_success(mock_user_event, mock_event_schema) -> None:
    # Arrange
    test_event_type = mock_user_event.event_type
    test_user_id = mock_user_event.user_id
    test_ip_address = mock_user_event.ip_address
    test_user_agent = mock_user_event.user_agent
    test_resource_type = mock_user_event.resource_type
    test_resource_id = mock_user_event.resource_id
    test_metadata = mock_user_event.metadata

    # Mock the database query - RULE #10 compliance: only operates on UserEvent model
    with (
        mock.patch.object(
            UserEvent, "create", new=mock.AsyncMock(return_value=mock_user_event)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_events.create_event.user_event_to_schema",
            new=mock.AsyncMock(return_value=mock_event_schema),
        ) as mock_converter,
    ):
        # Act
        result = await create_event(
            event_type=test_event_type,
            user_id=test_user_id,
            ip_address=test_ip_address,
            user_agent=test_user_agent,
            resource_type=test_resource_type,
            resource_id=test_resource_id,
            metadata=test_metadata,
        )

        # Assert
        assert result is not None
        assert result.id == mock_user_event.id
        assert result.user_id == test_user_id
        assert result.event_type == test_event_type
        assert result.ip_address == test_ip_address
        assert result.user_agent == test_user_agent
        assert result.resource_type == test_resource_type
        assert result.resource_id == test_resource_id
        assert result.metadata == test_metadata

        # Verify function calls
        mock_create.assert_called_once_with(
            user_id=test_user_id,
            event_type=test_event_type,
            ip_address=test_ip_address,
            user_agent=test_user_agent,
            resource_type=test_resource_type,
            resource_id=test_resource_id,
            metadata=test_metadata,
        )
        mock_converter.assert_called_once_with(mock_user_event)


@pytest.mark.asyncio
async def test_create_event_minimal() -> None:
    # Arrange
    test_event_type = "login_success"
    mock_event = mock.MagicMock(spec=UserEvent)
    mock_event.id = uuid.uuid4()
    mock_event.event_type = test_event_type
    mock_event.created_at = mock.MagicMock()
    mock_event.updated_at = mock.MagicMock()
    mock_event.fetch_related = mock.AsyncMock()

    mock_schema = UserEventSchema(
        id=mock_event.id,
        event_type=test_event_type,
        created_at=mock_event.created_at,
        updated_at=mock_event.updated_at,
    )

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "create", new=mock.AsyncMock(return_value=mock_event)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_events.create_event.user_event_to_schema",
            new=mock.AsyncMock(return_value=mock_schema),
        ) as mock_converter,
    ):
        # Act
        result = await create_event(event_type=test_event_type)

        # Assert
        assert result is not None
        assert result.id == mock_event.id
        assert result.event_type == test_event_type
        assert result.user_id is None
        assert result.ip_address is None
        assert result.user_agent is None
        assert result.resource_type is None
        assert result.resource_id is None
        assert result.metadata is None

        # Verify function calls
        mock_create.assert_called_once_with(
            user_id=None,
            event_type=test_event_type,
            ip_address=None,
            user_agent=None,
            resource_type=None,
            resource_id=None,
            metadata=None,
        )
        mock_converter.assert_called_once_with(mock_event)


@pytest.mark.asyncio
async def test_create_event_with_user_id_only() -> None:
    # Arrange
    test_event_type = "login_success"
    test_user_id = uuid.uuid4()
    mock_event = mock.MagicMock(spec=UserEvent)
    mock_event.id = uuid.uuid4()
    mock_event.event_type = test_event_type
    mock_event.user_id = test_user_id
    mock_event.created_at = mock.MagicMock()
    mock_event.updated_at = mock.MagicMock()
    mock_event.fetch_related = mock.AsyncMock()
    mock_event.user = mock.MagicMock()
    mock_event.user.id = test_user_id

    mock_schema = UserEventSchema(
        id=mock_event.id,
        user_id=test_user_id,
        event_type=test_event_type,
        created_at=mock_event.created_at,
        updated_at=mock_event.updated_at,
    )

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "create", new=mock.AsyncMock(return_value=mock_event)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_events.create_event.user_event_to_schema",
            new=mock.AsyncMock(return_value=mock_schema),
        ) as mock_converter,
    ):
        # Act
        result = await create_event(event_type=test_event_type, user_id=test_user_id)

        # Assert
        assert result is not None
        assert result.id == mock_event.id
        assert result.event_type == test_event_type
        assert result.user_id == test_user_id
        assert result.ip_address is None
        assert result.user_agent is None
        assert result.resource_type is None
        assert result.resource_id is None
        assert result.metadata is None

        # Verify function calls
        mock_create.assert_called_once_with(
            user_id=test_user_id,
            event_type=test_event_type,
            ip_address=None,
            user_agent=None,
            resource_type=None,
            resource_id=None,
            metadata=None,
        )
        mock_converter.assert_called_once_with(mock_event)


@pytest.mark.asyncio
async def test_create_event_with_metadata() -> None:
    # Arrange
    test_event_type = "login_success"
    test_metadata = {"key1": "value1", "key2": 123, "nested": {"inner": "value"}}
    mock_event = mock.MagicMock(spec=UserEvent)
    mock_event.id = uuid.uuid4()
    mock_event.event_type = test_event_type
    mock_event.metadata = test_metadata
    mock_event.created_at = mock.MagicMock()
    mock_event.updated_at = mock.MagicMock()
    mock_event.fetch_related = mock.AsyncMock()

    mock_schema = UserEventSchema(
        id=mock_event.id,
        event_type=test_event_type,
        metadata=test_metadata,
        created_at=mock_event.created_at,
        updated_at=mock_event.updated_at,
    )

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "create", new=mock.AsyncMock(return_value=mock_event)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_events.create_event.user_event_to_schema",
            new=mock.AsyncMock(return_value=mock_schema),
        ) as mock_converter,
    ):
        # Act
        result = await create_event(event_type=test_event_type, metadata=test_metadata)

        # Assert
        assert result is not None
        assert result.id == mock_event.id
        assert result.event_type == test_event_type
        assert result.metadata == test_metadata

        # Verify function calls
        mock_create.assert_called_once_with(
            user_id=None,
            event_type=test_event_type,
            ip_address=None,
            user_agent=None,
            resource_type=None,
            resource_id=None,
            metadata=test_metadata,
        )
        mock_converter.assert_called_once_with(mock_event)


@pytest.mark.asyncio
async def test_create_event_database_error() -> None:
    # Arrange
    test_event_type = "login_success"
    db_error = IntegrityError("Database error")

    # Mock the database query
    with mock.patch.object(
        UserEvent, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_event(event_type=test_event_type)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_create_event_converter_error(mock_user_event) -> None:
    # Arrange
    test_event_type = "login_success"
    converter_error = ValueError("Converter error")

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "create", new=mock.AsyncMock(return_value=mock_user_event)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_events.create_event.user_event_to_schema",
            new=mock.AsyncMock(side_effect=converter_error),
        ) as mock_converter,
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await create_event(event_type=test_event_type)

        # Verify the exception is propagated correctly
        assert exc_info.value == converter_error
        mock_create.assert_called_once()
        mock_converter.assert_called_once_with(mock_user_event)
