# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic_tag import TopicTag
from backend.db_functions.topic_tags.add_tags_to_topic import add_tags_to_topic


@pytest.mark.asyncio
async def test_add_tags_to_topic_success() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]

    mock_topic_tags = []
    for tag_id in tag_ids:
        mock_topic_tag = mock.MagicMock(spec=TopicTag)
        mock_topic_tag.topic_id = topic_id
        mock_topic_tag.tag_id = tag_id
        mock_topic_tags.append(mock_topic_tag)

    # Mock the database query - RULE #10 compliance: only operates on TopicTag model
    with (
        mock.patch.object(
            TopicTag, "get_or_none", new=mock.AsyncMock(return_value=None)
        ) as mock_get,
        mock.patch.object(
            TopicTag, "create", new=mock.AsyncMock(side_effect=mock_topic_tags)
        ) as mock_create,
    ):
        # Act
        result = await add_tags_to_topic(topic_id=topic_id, tag_ids=tag_ids)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == len(tag_ids)
        assert result == mock_topic_tags

        # Verify function calls
        assert mock_get.call_count == len(tag_ids)
        assert mock_create.call_count == len(tag_ids)
        for tag_id in tag_ids:
            mock_get.assert_any_call(topic_id=topic_id, tag_id=tag_id)
            mock_create.assert_any_call(topic_id=topic_id, tag_id=tag_id)


@pytest.mark.asyncio
async def test_add_tags_to_topic_with_existing_relationships() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]

    # First tag already exists, second and third are new
    existing_topic_tag = mock.MagicMock(spec=TopicTag)
    existing_topic_tag.topic_id = topic_id
    existing_topic_tag.tag_id = tag_ids[0]

    new_topic_tags = []
    for i in range(1, 3):
        mock_topic_tag = mock.MagicMock(spec=TopicTag)
        mock_topic_tag.topic_id = topic_id
        mock_topic_tag.tag_id = tag_ids[i]
        new_topic_tags.append(mock_topic_tag)

    # Mock the database query with different returns for each tag
    with (
        mock.patch.object(
            TopicTag,
            "get_or_none",
            new=mock.AsyncMock(side_effect=[existing_topic_tag, None, None]),
        ) as mock_get,
        mock.patch.object(
            TopicTag, "create", new=mock.AsyncMock(side_effect=new_topic_tags)
        ) as mock_create,
    ):
        # Act
        result = await add_tags_to_topic(topic_id=topic_id, tag_ids=tag_ids)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2  # Only 2 new relationships created
        assert result == new_topic_tags

        # Verify function calls
        assert mock_get.call_count == len(tag_ids)
        assert mock_create.call_count == 2  # Only 2 creates
        for i, tag_id in enumerate(tag_ids):
            mock_get.assert_any_call(topic_id=topic_id, tag_id=tag_id)

        # Verify create was only called for the second and third tags
        mock_create.assert_any_call(topic_id=topic_id, tag_id=tag_ids[1])
        mock_create.assert_any_call(topic_id=topic_id, tag_id=tag_ids[2])


@pytest.mark.asyncio
async def test_add_tags_to_topic_database_error_in_get() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_ids = [uuid.uuid4(), uuid.uuid4()]
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception during get_or_none
    with mock.patch.object(
        TopicTag, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await add_tags_to_topic(topic_id=topic_id, tag_ids=tag_ids)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(topic_id=topic_id, tag_id=tag_ids[0])


@pytest.mark.asyncio
async def test_add_tags_to_topic_database_error_in_create() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_ids = [uuid.uuid4(), uuid.uuid4()]
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception during create
    with (
        mock.patch.object(
            TopicTag, "get_or_none", new=mock.AsyncMock(return_value=None)
        ) as mock_get,
        mock.patch.object(
            TopicTag, "create", new=mock.AsyncMock(side_effect=db_error)
        ) as mock_create,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await add_tags_to_topic(topic_id=topic_id, tag_ids=tag_ids)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(topic_id=topic_id, tag_id=tag_ids[0])
        mock_create.assert_called_once_with(topic_id=topic_id, tag_id=tag_ids[0])
