# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db.models.topic_tag import TopicTag
from backend.db_functions.topic_tags.set_topic_tags import set_topic_tags


@pytest.fixture
def mock_existing_topic_tags() -> list[mock.MagicMock]:
    tags = []
    for i in range(2):
        topic_tag = mock.MagicMock(spec=TopicTag)
        topic_tag.tag = mock.MagicMock(spec=Tag)
        topic_tag.tag.id = uuid.uuid4()
        tags.append(topic_tag)
    return tags


@pytest.fixture
def mock_new_topic_tags() -> list[mock.MagicMock]:
    tags = []
    for i in range(2):
        topic_tag = mock.MagicMock(spec=TopicTag)
        topic_tag.topic_id = uuid.uuid4()
        topic_tag.tag_id = uuid.uuid4()
        tags.append(topic_tag)
    return tags


@pytest.mark.asyncio
async def test_set_topic_tags_success(
    mock_existing_topic_tags, mock_new_topic_tags
) -> None:
    # Arrange
    topic_id = uuid.uuid4()
    existing_tag_ids = [tt.tag.id for tt in mock_existing_topic_tags]

    # New tag IDs - one existing, two new
    new_tag_ids = [existing_tag_ids[0], uuid.uuid4(), uuid.uuid4()]

    # Tags to add (the two new ones)
    tags_to_add = [new_tag_ids[1], new_tag_ids[2]]

    # Tags to remove (one existing that's not in new_tag_ids)
    tags_to_remove = [existing_tag_ids[1]]

    removed_count = 1

    # Mock the database queries - RULE #10 compliance: operates on TopicTag model
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "prefetch_related",
            new=mock.AsyncMock(return_value=mock_existing_topic_tags),
        ) as mock_prefetch,
        mock.patch(
            "backend.db_functions.topic_tags.set_topic_tags.add_tags_to_topic",
            new=mock.AsyncMock(return_value=mock_new_topic_tags),
        ) as mock_add_tags,
        mock.patch(
            "backend.db_functions.topic_tags.set_topic_tags.remove_tags_from_topic",
            new=mock.AsyncMock(return_value=removed_count),
        ) as mock_remove_tags,
    ):
        # Act
        result = await set_topic_tags(topic_id=topic_id, tag_ids=new_tag_ids)

        # Assert
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == mock_new_topic_tags  # New tags added
        assert result[1] == removed_count  # Number of tags removed

        # Verify function calls
        mock_filter.assert_called_once_with(topic_id=topic_id)
        mock_prefetch.assert_called_once_with("tag")
        mock_add_tags.assert_called_once_with(topic_id, tags_to_add)
        mock_remove_tags.assert_called_once_with(topic_id, tags_to_remove)


@pytest.mark.asyncio
async def test_set_topic_tags_no_changes(mock_existing_topic_tags) -> None:
    # Arrange
    topic_id = uuid.uuid4()
    existing_tag_ids = [tt.tag.id for tt in mock_existing_topic_tags]

    # New tag IDs are exactly the same as existing
    new_tag_ids = existing_tag_ids

    # Mock the database queries with no changes needed
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "prefetch_related",
            new=mock.AsyncMock(return_value=mock_existing_topic_tags),
        ) as mock_prefetch,
        mock.patch(
            "backend.db_functions.topic_tags.set_topic_tags.add_tags_to_topic",
            new=mock.AsyncMock(return_value=[]),
        ) as mock_add_tags,
        mock.patch(
            "backend.db_functions.topic_tags.set_topic_tags.remove_tags_from_topic",
            new=mock.AsyncMock(return_value=0),
        ) as mock_remove_tags,
    ):
        # Act
        result = await set_topic_tags(topic_id=topic_id, tag_ids=new_tag_ids)

        # Assert
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == []  # No new tags added
        assert result[1] == 0  # No tags removed

        # Verify function calls
        mock_filter.assert_called_once_with(topic_id=topic_id)
        mock_prefetch.assert_called_once_with("tag")
        mock_add_tags.assert_called_once_with(
            topic_id, []
        )  # Empty list, no tags to add
        # remove_tags_from_topic should not be called since there are no tags to remove
        mock_remove_tags.assert_not_called()


@pytest.mark.asyncio
async def test_set_topic_tags_complete_replacement(
    mock_existing_topic_tags, mock_new_topic_tags
) -> None:
    # Arrange
    topic_id = uuid.uuid4()
    existing_tag_ids = [tt.tag.id for tt in mock_existing_topic_tags]

    # Completely new set of tag IDs
    new_tag_ids = [uuid.uuid4(), uuid.uuid4()]

    # All existing tags should be removed, all new tags should be added
    removed_count = len(existing_tag_ids)

    # Mock the database queries for complete replacement
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "prefetch_related",
            new=mock.AsyncMock(return_value=mock_existing_topic_tags),
        ) as mock_prefetch,
        mock.patch(
            "backend.db_functions.topic_tags.set_topic_tags.add_tags_to_topic",
            new=mock.AsyncMock(return_value=mock_new_topic_tags),
        ) as mock_add_tags,
        mock.patch(
            "backend.db_functions.topic_tags.set_topic_tags.remove_tags_from_topic",
            new=mock.AsyncMock(return_value=removed_count),
        ) as mock_remove_tags,
    ):
        # Act
        result = await set_topic_tags(topic_id=topic_id, tag_ids=new_tag_ids)

        # Assert
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == mock_new_topic_tags  # New tags added
        assert result[1] == removed_count  # All existing tags removed

        # Verify function calls
        mock_filter.assert_called_once_with(topic_id=topic_id)
        mock_prefetch.assert_called_once_with("tag")
        mock_add_tags.assert_called_once_with(topic_id, new_tag_ids)
        mock_remove_tags.assert_called_once_with(topic_id, existing_tag_ids)


@pytest.mark.asyncio
async def test_set_topic_tags_database_error_in_filter() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_ids = [uuid.uuid4(), uuid.uuid4()]
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception during filter
    with mock.patch.object(
        TopicTag, "filter", new=mock.MagicMock(side_effect=db_error)
    ) as mock_filter:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await set_topic_tags(topic_id=topic_id, tag_ids=tag_ids)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(topic_id=topic_id)


@pytest.mark.asyncio
async def test_set_topic_tags_error_in_add_tags(mock_existing_topic_tags) -> None:
    # Arrange
    topic_id = uuid.uuid4()
    new_tag_ids = [uuid.uuid4(), uuid.uuid4()]
    db_error = IntegrityError("Error adding tags")

    # Remove unused variable
    # Mock the database queries with error in add_tags_to_topic
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "prefetch_related",
            new=mock.AsyncMock(return_value=mock_existing_topic_tags),
        ) as mock_prefetch,
        mock.patch(
            "backend.db_functions.topic_tags.set_topic_tags.add_tags_to_topic",
            new=mock.AsyncMock(side_effect=db_error),
        ) as mock_add_tags,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await set_topic_tags(topic_id=topic_id, tag_ids=new_tag_ids)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(topic_id=topic_id)
        mock_prefetch.assert_called_once_with("tag")
        mock_add_tags.assert_called_once()


@pytest.mark.asyncio
async def test_set_topic_tags_error_in_remove_tags(
    mock_existing_topic_tags, mock_new_topic_tags
) -> None:
    # Arrange
    topic_id = uuid.uuid4()
    # Unused variable removed
    new_tag_ids = [uuid.uuid4(), uuid.uuid4()]
    db_error = IntegrityError("Error removing tags")

    # Mock the database queries with error in remove_tags_from_topic
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "prefetch_related",
            new=mock.AsyncMock(return_value=mock_existing_topic_tags),
        ) as mock_prefetch,
        mock.patch(
            "backend.db_functions.topic_tags.set_topic_tags.add_tags_to_topic",
            new=mock.AsyncMock(return_value=mock_new_topic_tags),
        ) as mock_add_tags,
        mock.patch(
            "backend.db_functions.topic_tags.set_topic_tags.remove_tags_from_topic",
            new=mock.AsyncMock(side_effect=db_error),
        ) as mock_remove_tags,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await set_topic_tags(topic_id=topic_id, tag_ids=new_tag_ids)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(topic_id=topic_id)
        mock_prefetch.assert_called_once_with("tag")
        mock_add_tags.assert_called_once()
        mock_remove_tags.assert_called_once()
