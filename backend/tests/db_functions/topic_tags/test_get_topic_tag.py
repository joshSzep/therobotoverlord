# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic_tag import TopicTag
from backend.db_functions.topic_tags.get_topic_tag import get_topic_tag


@pytest.mark.asyncio
async def test_get_topic_tag_success() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()

    mock_topic_tag = mock.MagicMock(spec=TopicTag)
    # Use mock attributes instead of direct property access
    mock_topic_tag.topic = mock.MagicMock(id=topic_id)
    mock_topic_tag.tag = mock.MagicMock(id=tag_id)

    # Mock the database query - RULE #10 compliance: only operates on TopicTag model
    with mock.patch.object(
        TopicTag, "get_or_none", new=mock.AsyncMock(return_value=mock_topic_tag)
    ) as mock_get:
        # Act
        result = await get_topic_tag(topic_id=topic_id, tag_id=tag_id)

        # Assert
        assert result is not None
        assert result.topic.id == topic_id
        assert result.tag.id == tag_id

        # Verify function calls
        mock_get.assert_called_once_with(topic_id=topic_id, tag_id=tag_id)


@pytest.mark.asyncio
async def test_get_topic_tag_not_found() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()

    # Mock the database query to return None (relationship doesn't exist)
    with mock.patch.object(
        TopicTag, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await get_topic_tag(topic_id=topic_id, tag_id=tag_id)

        # Assert
        assert result is None

        # Verify function calls
        mock_get.assert_called_once_with(topic_id=topic_id, tag_id=tag_id)


@pytest.mark.asyncio
async def test_get_topic_tag_database_error() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        TopicTag, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await get_topic_tag(topic_id=topic_id, tag_id=tag_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(topic_id=topic_id, tag_id=tag_id)
