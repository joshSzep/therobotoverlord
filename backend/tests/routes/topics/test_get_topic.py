# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.topics.get_topic import get_topic
from backend.schemas.topic import TopicResponse


@pytest.mark.asyncio
async def test_get_topic_success():
    """Test successful topic retrieval."""
    # Arrange
    topic_id = uuid.uuid4()

    # Create mock topic response
    mock_topic = mock.MagicMock(spec=TopicResponse)
    mock_topic.id = topic_id
    mock_topic.title = "Test Topic"
    mock_topic.description = "This is a test topic"
    mock_topic.created_at = datetime(2025, 5, 25)
    mock_topic.updated_at = datetime(2025, 5, 25)
    mock_topic.tags = []

    # Mock dependencies
    with mock.patch(
        "backend.routes.topics.get_topic.get_topic_by_id",
        new=mock.AsyncMock(return_value=mock_topic),
    ) as mock_get_topic_by_id:
        # Act
        result = await get_topic(topic_id=topic_id)

        # Assert
        assert result is mock_topic

        # Verify function calls
        mock_get_topic_by_id.assert_called_once_with(topic_id)


@pytest.mark.asyncio
async def test_get_topic_not_found():
    """Test topic retrieval with non-existent topic."""
    # Arrange
    topic_id = uuid.uuid4()

    # Mock dependencies - simulate topic not found
    with mock.patch(
        "backend.routes.topics.get_topic.get_topic_by_id",
        new=mock.AsyncMock(return_value=None),
    ) as mock_get_topic_by_id:
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_topic(topic_id=topic_id)

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Topic not found" in excinfo.value.detail

        # Verify function calls
        mock_get_topic_by_id.assert_called_once_with(topic_id)
