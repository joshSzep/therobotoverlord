# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db.models.topic_tag import TopicTag
from backend.db_functions.topic_tags.get_tags_for_topic import get_tags_for_topic
from backend.schemas.tag import TagResponse


@pytest.fixture
def mock_topic_tags() -> list[mock.MagicMock]:
    tags = []
    for i in range(3):
        topic_tag = mock.MagicMock(spec=TopicTag)
        topic_tag.tag = mock.MagicMock(spec=Tag)
        topic_tag.tag.id = uuid.uuid4()
        topic_tag.tag.name = f"Test Tag {i}"
        topic_tag.tag.slug = f"test-tag-{i}"
        tags.append(topic_tag)
    return tags


@pytest.fixture
def mock_tag_responses(mock_topic_tags) -> list[TagResponse]:
    return [
        TagResponse(id=tt.tag.id, name=tt.tag.name, slug=tt.tag.slug)
        for tt in mock_topic_tags
    ]


@pytest.mark.asyncio
async def test_get_tags_for_topic_success(mock_topic_tags, mock_tag_responses) -> None:
    # Arrange
    topic_id = uuid.uuid4()

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
            "backend.db_functions.topic_tags.get_tags_for_topic.tag_to_schema",
            new=mock.AsyncMock(side_effect=mock_tag_responses),
        ) as mock_converter,
    ):
        # Act
        result = await get_tags_for_topic(topic_id=topic_id)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == len(mock_topic_tags)
        assert result == mock_tag_responses

        # Verify function calls
        mock_filter.assert_called_once_with(topic_id=topic_id)
        mock_prefetch.assert_called_once_with("tag")
        assert mock_converter.call_count == len(mock_topic_tags)
        for i, tt in enumerate(mock_topic_tags):
            mock_converter.assert_any_call(tt.tag)


@pytest.mark.asyncio
async def test_get_tags_for_topic_empty_results() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    empty_tags = []

    # Mock the database query to return an empty list
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "prefetch_related",
            new=mock.AsyncMock(return_value=empty_tags),
        ) as mock_prefetch,
    ):
        # Act
        result = await get_tags_for_topic(topic_id=topic_id)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

        # Verify function calls
        mock_filter.assert_called_once_with(topic_id=topic_id)
        mock_prefetch.assert_called_once_with("tag")


@pytest.mark.asyncio
async def test_get_tags_for_topic_database_error() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        TopicTag, "filter", new=mock.MagicMock(side_effect=db_error)
    ) as mock_filter:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await get_tags_for_topic(topic_id=topic_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(topic_id=topic_id)
