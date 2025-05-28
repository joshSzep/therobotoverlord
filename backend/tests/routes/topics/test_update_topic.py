# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.topics.update_topic import update_topic
from backend.schemas.topic import TopicResponse
from backend.schemas.topic import TopicUpdate


@pytest.mark.asyncio
async def test_update_topic_success():
    """Test successful topic update."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id

    # Create mock topic
    mock_topic = mock.MagicMock(spec=TopicResponse)
    mock_topic.id = topic_id
    mock_topic.title = "Updated Topic"
    mock_topic.description = "This is an updated topic"
    mock_topic.created_at = datetime(2025, 5, 25)
    mock_topic.updated_at = datetime(2025, 5, 27)
    mock_topic.tags = []

    # Create update data
    topic_data = TopicUpdate(
        title="Updated Topic", description="This is an updated topic", tags=["test-tag"]
    )

    # Create mock tag
    mock_tag = mock.MagicMock()
    mock_tag.id = uuid.uuid4()
    mock_tag.name = "Test Tag"
    mock_tag.slug = "test-tag"

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.update_topic.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.update_topic.is_user_topic_author",
            new=mock.AsyncMock(return_value=True),
        ),
        mock.patch(
            "backend.routes.topics.update_topic.db_update_topic",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.update_topic.get_tag_by_slug",
            new=mock.AsyncMock(return_value=mock_tag),
        ),
        mock.patch(
            "backend.routes.topics.update_topic.create_tag",
            new=mock.AsyncMock(return_value=mock_tag),
        ),
        mock.patch(
            "backend.routes.topics.update_topic.set_topic_tags",
            new=mock.AsyncMock(),
        ),
        mock.patch(
            "backend.routes.topics.update_topic.slugify",
            return_value="test-tag",
        ),
    ):
        # Act
        result = await update_topic(
            topic_id=topic_id,
            topic_data=topic_data,
            current_user=mock_user,
        )

        # Assert
        assert result is mock_topic
        assert result.title == "Updated Topic"
        assert result.description == "This is an updated topic"


@pytest.mark.asyncio
async def test_update_topic_not_found():
    """Test topic update with non-existent topic."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id

    # Create update data
    topic_data = TopicUpdate(
        title="Updated Topic",
        description="This is an updated topic",
    )

    # Mock dependencies - simulate topic not found
    with mock.patch(
        "backend.routes.topics.update_topic.get_topic_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await update_topic(
                topic_id=topic_id,
                topic_data=topic_data,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Topic not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_update_topic_not_author():
    """Test topic update when user is not the author."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id

    # Create mock topic
    mock_topic = mock.MagicMock(spec=TopicResponse)
    mock_topic.id = topic_id

    # Create update data
    topic_data = TopicUpdate(
        title="Updated Topic",
        description="This is an updated topic",
    )

    # Mock dependencies - simulate user is not author
    with (
        mock.patch(
            "backend.routes.topics.update_topic.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.update_topic.is_user_topic_author",
            new=mock.AsyncMock(return_value=False),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await update_topic(
                topic_id=topic_id,
                topic_data=topic_data,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == 403
        assert "don't have permission" in excinfo.value.detail
