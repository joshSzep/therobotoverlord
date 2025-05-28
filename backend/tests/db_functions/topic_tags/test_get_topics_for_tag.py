# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic import Topic
from backend.db.models.topic_tag import TopicTag
from backend.db_functions.topic_tags.get_topics_for_tag import get_topics_for_tag
from backend.schemas.topic import TopicResponse


@pytest.fixture
def mock_topic_tags() -> list[mock.MagicMock]:
    tags = []
    for i in range(3):
        topic_tag = mock.MagicMock(spec=TopicTag)
        topic_tag.topic = mock.MagicMock(spec=Topic)
        topic_tag.topic.id = uuid.uuid4()
        topic_tag.topic.title = f"Test Topic {i}"
        topic_tag.topic.slug = f"test-topic-{i}"
        topic_tag.topic.content = f"Content for test topic {i}"
        tags.append(topic_tag)
    return tags


@pytest.fixture
def mock_topic_responses(mock_topic_tags) -> list[TopicResponse]:
    return [mock.MagicMock(spec=TopicResponse) for _ in mock_topic_tags]


@pytest.mark.asyncio
async def test_get_topics_for_tag_success(
    mock_topic_tags, mock_topic_responses
) -> None:
    # Arrange
    tag_id = uuid.uuid4()

    # Mock the database query - RULE #10 compliance: only operates on TopicTag model
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "prefetch_related",
            new=mock.AsyncMock(return_value=mock_topic_tags),
        ) as mock_prefetch,
        mock.patch(
            "backend.db_functions.topic_tags.get_topics_for_tag.topic_to_schema",
            new=mock.AsyncMock(side_effect=mock_topic_responses),
        ) as mock_converter,
    ):
        # Act
        result = await get_topics_for_tag(tag_id=tag_id)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == len(mock_topic_tags)
        assert result == mock_topic_responses

        # Verify function calls
        mock_filter.assert_called_once_with(tag_id=tag_id)
        mock_prefetch.assert_called_once_with("topic")
        assert mock_converter.call_count == len(mock_topic_tags)
        for i, tt in enumerate(mock_topic_tags):
            mock_converter.assert_any_call(tt.topic)


@pytest.mark.asyncio
async def test_get_topics_for_tag_empty_results() -> None:
    # Arrange
    tag_id = uuid.uuid4()
    empty_topics = []

    # Mock the database query to return an empty list
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "prefetch_related",
            new=mock.AsyncMock(return_value=empty_topics),
        ) as mock_prefetch,
    ):
        # Act
        result = await get_topics_for_tag(tag_id=tag_id)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

        # Verify function calls
        mock_filter.assert_called_once_with(tag_id=tag_id)
        mock_prefetch.assert_called_once_with("topic")


@pytest.mark.asyncio
async def test_get_topics_for_tag_database_error() -> None:
    # Arrange
    tag_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        TopicTag, "filter", new=mock.MagicMock(side_effect=db_error)
    ) as mock_filter:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await get_topics_for_tag(tag_id=tag_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(tag_id=tag_id)
