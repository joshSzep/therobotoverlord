"""Tests for the user_event_to_schema converter."""

from datetime import datetime
from unittest import mock
import uuid

import pytest

from backend.converters.user_event_to_schema import user_event_to_schema
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventSchema


@pytest.fixture
def mock_user_event() -> mock.MagicMock:
    """Return a mock user event for testing."""
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create a mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id

    # Create a mock event
    event = mock.MagicMock(spec=UserEvent)
    event.id = event_id
    event.event_type = "login"
    event.ip_address = "127.0.0.1"
    event.user_agent = "Test User Agent"
    event.resource_type = "user"
    event.resource_id = uuid.uuid4()
    event.metadata = {"success": True}
    event.created_at = datetime.now()
    event.updated_at = datetime.now()

    # Set up the user relation
    event.user = mock_user
    event.fetch_related = mock.AsyncMock()

    return event


@pytest.mark.asyncio
async def test_user_event_to_schema_with_user(mock_user_event) -> None:
    """Test user_event_to_schema with a user."""
    # Convert the mock event to a schema
    schema = await user_event_to_schema(mock_user_event)

    # Verify fetch_related was called
    mock_user_event.fetch_related.assert_awaited_once_with("user")

    # Verify the schema has the correct values
    assert isinstance(schema, UserEventSchema)
    assert schema.id == mock_user_event.id
    assert schema.user_id == mock_user_event.user.id
    assert schema.event_type == mock_user_event.event_type
    assert schema.ip_address == mock_user_event.ip_address
    assert schema.user_agent == mock_user_event.user_agent
    assert schema.resource_type == mock_user_event.resource_type
    assert schema.resource_id == mock_user_event.resource_id
    assert schema.metadata == mock_user_event.metadata
    assert schema.created_at == mock_user_event.created_at
    assert schema.updated_at == mock_user_event.updated_at


@pytest.mark.asyncio
async def test_user_event_to_schema_without_user() -> None:
    """Test user_event_to_schema without a user."""
    # Create a mock event without a user
    event_id = uuid.uuid4()
    event = mock.MagicMock(spec=UserEvent)
    event.id = event_id
    event.event_type = "system"
    event.ip_address = "127.0.0.1"
    event.user_agent = "Test User Agent"
    event.resource_type = "system"
    event.resource_id = None
    event.metadata = {"action": "maintenance"}
    event.created_at = datetime.now()
    event.updated_at = datetime.now()

    # Set up the user relation to be None
    event.user = None
    event.fetch_related = mock.AsyncMock()

    # Convert the mock event to a schema
    schema = await user_event_to_schema(event)

    # Verify fetch_related was called
    event.fetch_related.assert_awaited_once_with("user")

    # Verify the schema has the correct values
    assert isinstance(schema, UserEventSchema)
    assert schema.id == event.id
    assert schema.user_id is None
    assert schema.event_type == event.event_type
    assert schema.ip_address == event.ip_address
    assert schema.user_agent == event.user_agent
    assert schema.resource_type == event.resource_type
    assert schema.resource_id is None
    assert schema.metadata == event.metadata
    assert schema.created_at == event.created_at
    assert schema.updated_at == event.updated_at


@pytest.mark.asyncio
async def test_user_event_to_schema_without_metadata() -> None:
    """Test user_event_to_schema without metadata."""
    # Create a mock event without metadata
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create a mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id

    # Create a mock event
    event = mock.MagicMock(spec=UserEvent)
    event.id = event_id
    event.event_type = "login"
    event.ip_address = "127.0.0.1"
    event.user_agent = "Test User Agent"
    event.resource_type = "user"
    event.resource_id = uuid.uuid4()
    event.metadata = None
    event.created_at = datetime.now()
    event.updated_at = datetime.now()

    # Set up the user relation
    event.user = mock_user
    event.fetch_related = mock.AsyncMock()

    # Convert the mock event to a schema
    schema = await user_event_to_schema(event)

    # Verify fetch_related was called
    event.fetch_related.assert_awaited_once_with("user")

    # Verify the schema has the correct values
    assert isinstance(schema, UserEventSchema)
    assert schema.id == event.id
    assert schema.user_id == event.user.id
    assert schema.event_type == event.event_type
    assert schema.ip_address == event.ip_address
    assert schema.user_agent == event.user_agent
    assert schema.resource_type == event.resource_type
    assert schema.resource_id == event.resource_id
    assert schema.metadata == {}
    assert schema.created_at == event.created_at
    assert schema.updated_at == event.updated_at
