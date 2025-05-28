# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.topics.delete_topic import delete_topic


@pytest.mark.asyncio
async def test_delete_topic_success():
    """Test successful topic deletion."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.delete_topic.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.delete_topic.is_user_topic_author",
            new=mock.AsyncMock(return_value=True),
        ),
        mock.patch(
            "backend.routes.topics.delete_topic.db_delete_topic",
            new=mock.AsyncMock(return_value=True),
        ),
    ):
        # Act
        result = await delete_topic(
            topic_id=topic_id,
            current_user=mock_user,
        )

        # Assert
        assert result is None  # Function returns None on success


@pytest.mark.asyncio
async def test_delete_topic_not_found():
    """Test topic deletion with non-existent topic."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id

    # Mock dependencies - simulate topic not found
    with mock.patch(
        "backend.routes.topics.delete_topic.get_topic_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_topic(
                topic_id=topic_id,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Topic not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_topic_not_author():
    """Test topic deletion when user is not the author."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Mock dependencies - simulate user is not author
    with (
        mock.patch(
            "backend.routes.topics.delete_topic.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.delete_topic.is_user_topic_author",
            new=mock.AsyncMock(return_value=False),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_topic(
                topic_id=topic_id,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == 403
        assert "don't have permission" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_topic_failure():
    """Test topic deletion with database failure."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Mock dependencies - simulate deletion failure
    with (
        mock.patch(
            "backend.routes.topics.delete_topic.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.delete_topic.is_user_topic_author",
            new=mock.AsyncMock(return_value=True),
        ),
        mock.patch(
            "backend.routes.topics.delete_topic.db_delete_topic",
            new=mock.AsyncMock(return_value=False),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_topic(
                topic_id=topic_id,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == 500
        assert "Failed to delete topic" in excinfo.value.detail
