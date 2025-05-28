# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.user_event import UserEvent
from backend.db_functions.user_events.log_login_success import log_login_success
from backend.schemas.user_event import UserEventSchema


@pytest.fixture
def mock_user_event() -> mock.MagicMock:
    event = mock.MagicMock(spec=UserEvent)
    event.id = uuid.uuid4()
    event.user_id = uuid.uuid4()
    event.event_type = "login"
    event.ip_address = "192.168.1.1"
    event.user_agent = "Mozilla/5.0"
    event.metadata = {"success": True}
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
        metadata=mock_user_event.metadata,
        created_at=mock_user_event.created_at,
        updated_at=mock_user_event.updated_at,
    )


@pytest.mark.asyncio
async def test_log_login_success(mock_user_event, mock_event_schema) -> None:
    # Arrange
    test_user_id = mock_user_event.user_id
    test_ip_address = mock_user_event.ip_address
    test_user_agent = mock_user_event.user_agent

    # Mock the database query - RULE #10 compliance: only operates on UserEvent model
    with (
        mock.patch.object(
            UserEvent, "create", new=mock.AsyncMock(return_value=mock_user_event)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_events.log_login_success.user_event_to_schema",
            new=mock.AsyncMock(return_value=mock_event_schema),
        ) as mock_converter,
    ):
        # Act
        result = await log_login_success(
            user_id=test_user_id,
            ip_address=test_ip_address,
            user_agent=test_user_agent,
        )

        # Assert
        assert result is not None
        assert result.id == mock_user_event.id
        assert result.user_id == test_user_id
        assert result.event_type == "login"
        assert result.ip_address == test_ip_address
        assert result.user_agent == test_user_agent
        assert result.metadata == {"success": True}

        # Verify function calls
        mock_create.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
            ip_address=test_ip_address,
            user_agent=test_user_agent,
            metadata={"success": True},
        )
        mock_converter.assert_called_once_with(mock_user_event)


@pytest.mark.asyncio
async def test_log_login_success_database_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_ip_address = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    db_error = IntegrityError("Database error")

    # Mock the database query
    with mock.patch.object(
        UserEvent, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await log_login_success(
                user_id=test_user_id,
                ip_address=test_ip_address,
                user_agent=test_user_agent,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once_with(
            user_id=test_user_id,
            event_type="login",
            ip_address=test_ip_address,
            user_agent=test_user_agent,
            metadata={"success": True},
        )


@pytest.mark.asyncio
async def test_log_login_success_converter_error(mock_user_event) -> None:
    # Arrange
    test_user_id = mock_user_event.user_id
    test_ip_address = mock_user_event.ip_address
    test_user_agent = mock_user_event.user_agent
    converter_error = ValueError("Converter error")

    # Mock the database query
    with (
        mock.patch.object(
            UserEvent, "create", new=mock.AsyncMock(return_value=mock_user_event)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_events.log_login_success.user_event_to_schema",
            new=mock.AsyncMock(side_effect=converter_error),
        ) as mock_converter,
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await log_login_success(
                user_id=test_user_id,
                ip_address=test_ip_address,
                user_agent=test_user_agent,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == converter_error
        mock_create.assert_called_once()
        mock_converter.assert_called_once_with(mock_user_event)
