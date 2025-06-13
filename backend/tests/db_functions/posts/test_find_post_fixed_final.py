"""
Tests for find_post_from_pending_post function.
"""

from unittest import mock
import uuid

import pytest

from backend.db.models.pending_post import PendingPost

# Import the function and its dependencies directly
from backend.db_functions.posts.find_post_from_pending_post import (
    find_post_from_pending_post,
)


@pytest.fixture
def setup_mocks(monkeypatch):
    """Set up mocks for all tests."""
    # Create mock objects
    mock_pending_post_get_or_none = mock.AsyncMock()
    mock_get_post_approval_event = mock.AsyncMock()
    mock_get_post_by_id = mock.AsyncMock()

    # Apply monkeypatches
    monkeypatch.setattr(PendingPost, "get_or_none", mock_pending_post_get_or_none)
    monkeypatch.setattr(
        "backend.db_functions.posts.find_post_from_pending_post.get_post_approval_event",
        mock_get_post_approval_event,
    )
    monkeypatch.setattr(
        "backend.db_functions.posts.find_post_from_pending_post.get_post_by_id",
        mock_get_post_by_id,
    )

    # Return the mocks for use in tests
    return {
        "mock_pending_post": mock_pending_post_get_or_none,
        "mock_get_event": mock_get_post_approval_event,
        "mock_get_post": mock_get_post_by_id,
    }


@pytest.mark.asyncio
async def test_pending_post_still_exists(setup_mocks):
    """Test that None is returned when the pending post still exists."""
    # Arrange
    pending_post_id = uuid.uuid4()
    mock_pending_post = mock.MagicMock()
    setup_mocks["mock_pending_post"].return_value = mock_pending_post

    # Act
    result = await find_post_from_pending_post(pending_post_id)

    # Assert
    assert result is None
    setup_mocks["mock_pending_post"].assert_called_once_with(id=pending_post_id)
    setup_mocks["mock_get_event"].assert_not_called()
    setup_mocks["mock_get_post"].assert_not_called()


@pytest.mark.asyncio
async def test_find_post_when_pending_post_approved(setup_mocks):
    """Test finding an approved post when the pending post has been approved."""
    # Arrange
    pending_post_id = uuid.uuid4()
    approved_post_id = uuid.uuid4()
    mock_approved_post = mock.MagicMock()

    # Configure mocks
    setup_mocks["mock_pending_post"].return_value = None

    mock_event = mock.MagicMock()
    mock_event.metadata = {"approved_post_id": str(approved_post_id)}
    setup_mocks["mock_get_event"].return_value = mock_event

    setup_mocks["mock_get_post"].return_value = mock_approved_post

    # Act
    result = await find_post_from_pending_post(pending_post_id)

    # Assert
    assert result is mock_approved_post
    setup_mocks["mock_pending_post"].assert_called_once_with(id=pending_post_id)
    setup_mocks["mock_get_event"].assert_called_once_with(pending_post_id)
    setup_mocks["mock_get_post"].assert_called_once_with(approved_post_id)


@pytest.mark.asyncio
async def test_no_approval_event(setup_mocks):
    """Test when pending post doesn't exist but no approval event is found."""
    # Arrange
    pending_post_id = uuid.uuid4()
    setup_mocks["mock_pending_post"].return_value = None
    setup_mocks["mock_get_event"].return_value = None

    # Act
    result = await find_post_from_pending_post(pending_post_id)

    # Assert
    assert result is None
    setup_mocks["mock_pending_post"].assert_called_once_with(id=pending_post_id)
    setup_mocks["mock_get_event"].assert_called_once_with(pending_post_id)
    setup_mocks["mock_get_post"].assert_not_called()


@pytest.mark.asyncio
async def test_approval_event_has_no_metadata(setup_mocks):
    """Test when approval event exists but has no metadata."""
    # Arrange
    pending_post_id = uuid.uuid4()
    setup_mocks["mock_pending_post"].return_value = None

    mock_event = mock.MagicMock()
    mock_event.metadata = None
    setup_mocks["mock_get_event"].return_value = mock_event

    # Act
    result = await find_post_from_pending_post(pending_post_id)

    # Assert
    assert result is None
    setup_mocks["mock_pending_post"].assert_called_once_with(id=pending_post_id)
    setup_mocks["mock_get_event"].assert_called_once_with(pending_post_id)
    setup_mocks["mock_get_post"].assert_not_called()


@pytest.mark.asyncio
async def test_approval_event_has_invalid_uuid(setup_mocks):
    """Test when approval event has invalid UUID in metadata."""
    # Arrange
    pending_post_id = uuid.uuid4()
    setup_mocks["mock_pending_post"].return_value = None

    mock_event = mock.MagicMock()
    mock_event.metadata = {"approved_post_id": "not-a-valid-uuid"}
    setup_mocks["mock_get_event"].return_value = mock_event

    # Act
    result = await find_post_from_pending_post(pending_post_id)

    # Assert
    assert result is None
    setup_mocks["mock_pending_post"].assert_called_once_with(id=pending_post_id)
    setup_mocks["mock_get_event"].assert_called_once_with(pending_post_id)
    setup_mocks["mock_get_post"].assert_not_called()


@pytest.mark.asyncio
async def test_approved_post_not_found(setup_mocks):
    """Test when approved post ID is valid but post is not found."""
    # Arrange
    pending_post_id = uuid.uuid4()
    approved_post_id = uuid.uuid4()

    setup_mocks["mock_pending_post"].return_value = None

    mock_event = mock.MagicMock()
    mock_event.metadata = {"approved_post_id": str(approved_post_id)}
    setup_mocks["mock_get_event"].return_value = mock_event

    setup_mocks["mock_get_post"].return_value = None

    # Act
    result = await find_post_from_pending_post(pending_post_id)

    # Assert
    assert result is None
    setup_mocks["mock_pending_post"].assert_called_once_with(id=pending_post_id)
    setup_mocks["mock_get_event"].assert_called_once_with(pending_post_id)
    setup_mocks["mock_get_post"].assert_called_once_with(approved_post_id)


@pytest.mark.asyncio
async def test_exception_occurs(setup_mocks):
    """Test handling of exceptions during processing."""
    # Arrange
    pending_post_id = uuid.uuid4()
    setup_mocks["mock_pending_post"].side_effect = Exception("Test exception")

    # Act
    result = await find_post_from_pending_post(pending_post_id)

    # Assert
    assert result is None
    setup_mocks["mock_pending_post"].assert_called_once_with(id=pending_post_id)
    setup_mocks["mock_get_event"].assert_not_called()
    setup_mocks["mock_get_post"].assert_not_called()
