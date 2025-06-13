# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
import pytest

# Project-specific imports
from backend.converters.user_event_to_schema import user_event_to_schema
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventResponse


@pytest.fixture
def mock_user_event() -> mock.MagicMock:
    """Create a mock user event for testing."""
    event = mock.MagicMock(spec=UserEvent)
    event.id = uuid.uuid4()
    event.event_type = "post_created"
    event.resource_type = "post"
    event.resource_id = uuid.uuid4()
    event.metadata = {"post_content": "Test content"}
    event.created_at = datetime.now()
    event.updated_at = datetime.now()

    # Mock user relation
    user = mock.MagicMock()
    user.id = uuid.uuid4()
    event.user = user

    # Mock fetch_related method
    event.fetch_related = mock.AsyncMock()

    return event


@pytest.mark.asyncio
async def test_user_event_to_schema_basic(mock_user_event):
    """Test basic conversion of a user event to a schema."""
    # Act
    result = await user_event_to_schema(mock_user_event)

    # Assert
    assert isinstance(result, UserEventResponse)
    assert result.id == mock_user_event.id
    assert result.user_id == mock_user_event.user.id
    assert result.event_type == mock_user_event.event_type
    assert result.resource_type == mock_user_event.resource_type
    assert result.resource_id == mock_user_event.resource_id
    assert result.metadata == mock_user_event.metadata
    assert result.created_at == mock_user_event.created_at
    assert result.updated_at == mock_user_event.updated_at

    # Verify function calls
    mock_user_event.fetch_related.assert_awaited_once_with("user")


@pytest.mark.asyncio
async def test_user_event_to_schema_no_user(mock_user_event):
    """Test conversion of a user event with no user relation."""
    # Arrange
    mock_user_event.user = None

    # Act
    result = await user_event_to_schema(mock_user_event)

    # Assert
    assert result.user_id is None

    # Verify function calls
    mock_user_event.fetch_related.assert_awaited_once_with("user")


@pytest.mark.asyncio
async def test_user_event_to_schema_no_metadata(mock_user_event):
    """Test conversion of a user event with no metadata."""
    # Arrange
    mock_user_event.metadata = None

    # Act
    result = await user_event_to_schema(mock_user_event)

    # Assert
    assert result.metadata == {}

    # Verify function calls
    mock_user_event.fetch_related.assert_awaited_once_with("user")


@pytest.mark.asyncio
async def test_user_event_to_schema_different_event_types():
    """Test conversion with different event types."""
    # Arrange
    event_types = [
        ("post_created", "post"),
        ("post_approved", "post"),
        ("post_rejected", "post"),
        ("user_registered", "user"),
        ("user_locked", "user"),
        ("topic_created", "topic"),
    ]

    for event_type, resource_type in event_types:
        # Create mock event with specific type
        event = mock.MagicMock(spec=UserEvent)
        event.id = uuid.uuid4()
        event.event_type = event_type
        event.resource_type = resource_type
        event.resource_id = uuid.uuid4()
        event.metadata = {"test": "data"}
        event.created_at = datetime.now()
        event.updated_at = datetime.now()

        # Mock user relation
        user = mock.MagicMock()
        user.id = uuid.uuid4()
        event.user = user

        # Mock fetch_related method
        event.fetch_related = mock.AsyncMock()

        # Act
        result = await user_event_to_schema(event)

        # Assert
        assert result.event_type == event_type
        assert result.resource_type == resource_type


@pytest.mark.asyncio
async def test_user_event_to_schema_different_metadata():
    """Test conversion with different metadata structures."""
    # Arrange
    test_metadata = [
        {"post_content": "Test content"},
        {"reason": "Content violates guidelines"},
        {"topic_id": str(uuid.uuid4())},
        {},  # Empty metadata
        {"nested": {"key": "value"}},  # Nested metadata
    ]

    for metadata in test_metadata:
        # Create mock event with specific metadata
        event = mock.MagicMock(spec=UserEvent)
        event.id = uuid.uuid4()
        event.event_type = "test_event"
        event.resource_type = "test_resource"
        event.resource_id = uuid.uuid4()
        event.metadata = metadata
        event.created_at = datetime.now()
        event.updated_at = datetime.now()

        # Mock user relation
        user = mock.MagicMock()
        user.id = uuid.uuid4()
        event.user = user

        # Mock fetch_related method
        event.fetch_related = mock.AsyncMock()

        # Act
        result = await user_event_to_schema(event)

        # Assert
        assert result.metadata == metadata


@pytest.mark.asyncio
async def test_user_event_to_schema_fetch_related_error():
    """Test handling when fetch_related fails."""
    # Arrange
    event = mock.MagicMock(spec=UserEvent)
    event.id = uuid.uuid4()

    # Mock fetch_related to fail
    fetch_error = Exception("Failed to fetch related user")
    event.fetch_related = mock.AsyncMock(side_effect=fetch_error)

    # Act and Assert
    with pytest.raises(Exception) as exc_info:
        await user_event_to_schema(event)

    # Verify the error is propagated
    assert exc_info.value == fetch_error
    event.fetch_related.assert_awaited_once_with("user")
