# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic_tag import TopicTag
from backend.db_functions.topic_tags.create_topic_tag import create_topic_tag


@pytest.mark.asyncio
async def test_create_topic_tag_success() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()

    mock_topic_tag = mock.MagicMock(spec=TopicTag)
    mock_topic_tag.topic_id = topic_id
    mock_topic_tag.tag_id = tag_id

    # Mock the database query - RULE #10 compliance: only operates on TopicTag model
    with mock.patch.object(
        TopicTag, "create", new=mock.AsyncMock(return_value=mock_topic_tag)
    ) as mock_create:
        # Act
        result = await create_topic_tag(topic_id=topic_id, tag_id=tag_id)

        # Assert
        assert result is not None
        assert result.topic_id == topic_id
        assert result.tag_id == tag_id

        # Verify function calls
        mock_create.assert_called_once_with(topic_id=topic_id, tag_id=tag_id)


@pytest.mark.asyncio
async def test_create_topic_tag_duplicate_relationship() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()
    db_error = IntegrityError("Duplicate entry")

    # Mock the database query to raise an integrity error (duplicate relationship)
    with mock.patch.object(
        TopicTag, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_topic_tag(topic_id=topic_id, tag_id=tag_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once_with(topic_id=topic_id, tag_id=tag_id)


@pytest.mark.asyncio
async def test_create_topic_tag_invalid_foreign_key() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()
    db_error = IntegrityError("Foreign key constraint failed")

    # Mock the database query to raise an integrity error (invalid foreign key)
    with mock.patch.object(
        TopicTag, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_topic_tag(topic_id=topic_id, tag_id=tag_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once_with(topic_id=topic_id, tag_id=tag_id)
