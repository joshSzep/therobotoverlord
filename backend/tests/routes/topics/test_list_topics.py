# Standard library imports
from datetime import datetime
from typing import List
from typing import cast
from unittest import mock
import uuid

# Third-party imports
import pytest

# Project-specific imports
from backend.routes.topics.list_topics import list_topics
from backend.schemas.topic import TopicList
from backend.schemas.topic import TopicResponse


@pytest.mark.asyncio
async def test_list_topics_success():
    """Test successful listing of all topics."""
    # Arrange
    mock_topics = [
        mock.MagicMock(spec=TopicResponse),
        mock.MagicMock(spec=TopicResponse),
    ]

    # Configure mock topics
    for i, topic in enumerate(mock_topics):
        topic.id = uuid.uuid4()
        topic.title = f"Test Topic {i + 1}"
        topic.description = f"This is test topic {i + 1}"
        topic.created_at = datetime(2025, 5, 25)
        topic.updated_at = datetime(2025, 5, 25)
        topic.tags = []

    # Cast mock_topics to the expected type
    topics_list = cast(List[TopicResponse], mock_topics)
    mock_topic_list = TopicList(topics=topics_list, count=len(mock_topics))

    # Mock dependencies
    with mock.patch(
        "backend.routes.topics.list_topics.db_list_topics",
        new=mock.AsyncMock(return_value=mock_topic_list),
    ) as mock_db_list_topics:
        # Act
        result = await list_topics(skip=0, limit=10)

        # Assert
        assert result is mock_topic_list
        assert len(result.topics) == 2
        assert result.count == 2

        # Verify function calls
        mock_db_list_topics.assert_called_once_with(skip=0, limit=10)


@pytest.mark.asyncio
async def test_list_topics_with_pagination():
    """Test listing topics with pagination."""
    # Arrange
    mock_topics = [
        mock.MagicMock(spec=TopicResponse),
        mock.MagicMock(spec=TopicResponse),
    ]

    # Configure mock topics
    for i, topic in enumerate(mock_topics):
        topic.id = uuid.uuid4()
        topic.title = f"Test Topic {i + 1}"
        topic.description = f"This is test topic {i + 1}"
        topic.created_at = datetime(2025, 5, 25)
        topic.updated_at = datetime(2025, 5, 25)
        topic.tags = []

    # Cast mock_topics to the expected type
    topics_list = cast(List[TopicResponse], mock_topics)
    mock_topic_list = TopicList(topics=topics_list, count=len(mock_topics))

    # Mock dependencies
    with mock.patch(
        "backend.routes.topics.list_topics.db_list_topics",
        new=mock.AsyncMock(return_value=mock_topic_list),
    ) as mock_db_list_topics:
        # Act
        result = await list_topics(skip=1, limit=5)

        # Assert
        assert result is mock_topic_list

        # Verify function calls with correct pagination parameters
        mock_db_list_topics.assert_called_once_with(skip=1, limit=5)


@pytest.mark.asyncio
async def test_list_topics_with_tag_found():
    """Test listing topics filtered by tag that exists."""
    # Arrange
    tag_id = uuid.uuid4()
    mock_tag = mock.MagicMock()
    mock_tag.id = tag_id
    mock_tag.name = "Test Tag"
    mock_tag.slug = "test-tag"

    mock_topics = [
        mock.MagicMock(spec=TopicResponse),
        mock.MagicMock(spec=TopicResponse),
    ]

    # Configure mock topics
    for i, topic in enumerate(mock_topics):
        topic.id = uuid.uuid4()
        topic.title = f"Test Topic {i + 1}"
        topic.description = f"This is test topic {i + 1}"
        topic.created_at = datetime(2025, 5, 25)
        topic.updated_at = datetime(2025, 5, 25)
        topic.tags = [mock_tag]

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.list_topics.get_tag_by_slug",
            new=mock.AsyncMock(return_value=mock_tag),
        ),
        mock.patch(
            "backend.routes.topics.list_topics.get_tag_by_name",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.routes.topics.list_topics.get_topics_for_tag",
            new=mock.AsyncMock(return_value=mock_topics),
        ) as mock_get_topics_for_tag,
    ):
        # Act
        result = await list_topics(skip=0, limit=10, tag="test-tag")

        # Assert
        assert isinstance(result, TopicList)
        assert len(result.topics) == 2
        assert result.count == 2

        # Verify function calls
        mock_get_topics_for_tag.assert_called_once_with(tag_id)


@pytest.mark.asyncio
async def test_list_topics_with_tag_by_name():
    """Test listing topics filtered by tag name."""
    # Arrange
    tag_id = uuid.uuid4()
    mock_tag = mock.MagicMock()
    mock_tag.id = tag_id
    mock_tag.name = "Test Tag"
    mock_tag.slug = "test-tag"

    mock_topics = [mock.MagicMock(spec=TopicResponse)]

    # Configure mock topic
    mock_topics[0].id = uuid.uuid4()
    mock_topics[0].title = "Test Topic"
    mock_topics[0].description = "This is a test topic"
    mock_topics[0].created_at = datetime(2025, 5, 25)
    mock_topics[0].updated_at = datetime(2025, 5, 25)
    mock_topics[0].tags = [mock_tag]

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.list_topics.get_tag_by_slug",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.routes.topics.list_topics.get_tag_by_name",
            new=mock.AsyncMock(return_value=mock_tag),
        ),
        mock.patch(
            "backend.routes.topics.list_topics.get_topics_for_tag",
            new=mock.AsyncMock(return_value=mock_topics),
        ) as mock_get_topics_for_tag,
    ):
        # Act
        result = await list_topics(skip=0, limit=10, tag="Test Tag")

        # Assert
        assert isinstance(result, TopicList)
        assert len(result.topics) == 1
        assert result.count == 1

        # Verify function calls
        mock_get_topics_for_tag.assert_called_once_with(tag_id)


@pytest.mark.asyncio
async def test_list_topics_with_tag_not_found():
    """Test listing topics with a non-existent tag."""
    # Arrange
    # Mock dependencies to return None for both tag lookups
    with (
        mock.patch(
            "backend.routes.topics.list_topics.get_tag_by_slug",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.routes.topics.list_topics.get_tag_by_name",
            new=mock.AsyncMock(return_value=None),
        ),
    ):
        # Act
        result = await list_topics(skip=0, limit=10, tag="non-existent-tag")

        # Assert
        assert isinstance(result, TopicList)
        assert len(result.topics) == 0
        assert result.count == 0
