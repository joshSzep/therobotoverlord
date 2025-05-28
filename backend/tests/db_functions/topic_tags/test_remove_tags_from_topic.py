# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic_tag import TopicTag
from backend.db_functions.topic_tags.remove_tags_from_topic import (
    remove_tags_from_topic,
)


@pytest.mark.asyncio
async def test_remove_tags_from_topic_success() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
    deleted_count = 3

    # Mock the database query - RULE #10 compliance: only operates on TopicTag model
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "delete",
            new=mock.AsyncMock(return_value=deleted_count),
        ) as mock_delete,
    ):
        # Act
        result = await remove_tags_from_topic(topic_id=topic_id, tag_ids=tag_ids)

        # Assert
        assert result == deleted_count

        # Verify function calls
        mock_filter.assert_called_once_with(topic_id=topic_id, tag__id__in=tag_ids)
        mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_remove_tags_from_topic_no_tags_deleted() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_ids = [uuid.uuid4(), uuid.uuid4()]
    deleted_count = 0

    # Mock the database query with no tags deleted
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "delete",
            new=mock.AsyncMock(return_value=deleted_count),
        ) as mock_delete,
    ):
        # Act
        result = await remove_tags_from_topic(topic_id=topic_id, tag_ids=tag_ids)

        # Assert
        assert result == deleted_count

        # Verify function calls
        mock_filter.assert_called_once_with(topic_id=topic_id, tag__id__in=tag_ids)
        mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_remove_tags_from_topic_database_error() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_ids = [uuid.uuid4(), uuid.uuid4()]
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        TopicTag, "filter", new=mock.MagicMock(side_effect=db_error)
    ) as mock_filter:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await remove_tags_from_topic(topic_id=topic_id, tag_ids=tag_ids)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(topic_id=topic_id, tag__id__in=tag_ids)


@pytest.mark.asyncio
async def test_remove_tags_from_topic_delete_error() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    tag_ids = [uuid.uuid4(), uuid.uuid4()]
    db_error = IntegrityError("Delete operation failed")

    # Mock the database query with delete raising an exception
    with (
        mock.patch.object(
            TopicTag, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value, "delete", new=mock.AsyncMock(side_effect=db_error)
        ) as mock_delete,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await remove_tags_from_topic(topic_id=topic_id, tag_ids=tag_ids)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(topic_id=topic_id, tag__id__in=tag_ids)
        mock_delete.assert_called_once()
