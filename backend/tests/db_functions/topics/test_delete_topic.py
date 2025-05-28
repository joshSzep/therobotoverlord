# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic import Topic
from backend.db_functions.topics.delete_topic import delete_topic


@pytest.fixture
def mock_topic() -> mock.MagicMock:
    topic = mock.MagicMock(spec=Topic)
    topic.id = uuid.uuid4()
    topic.title = "Test Topic"
    topic.description = "Test Description"
    topic.author_id = uuid.uuid4()
    return topic


@pytest.mark.asyncio
async def test_delete_topic_success(mock_topic) -> None:
    # Arrange
    test_id = mock_topic.id

    # Mock the database query - RULE #10 compliance: only operates on Topic model
    with (
        mock.patch.object(
            Topic, "get_or_none", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_get,
        mock.patch.object(mock_topic, "delete", new=mock.AsyncMock()) as mock_delete,
    ):
        # Act
        result = await delete_topic(test_id)

        # Assert
        assert result is True

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_topic_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()

    # Mock the database query
    with mock.patch.object(
        Topic, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await delete_topic(test_id)

        # Assert
        assert result is False
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_delete_topic_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Topic, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await delete_topic(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_delete_topic_delete_error(mock_topic) -> None:
    # Arrange
    test_id = mock_topic.id
    delete_error = IntegrityError("Error deleting topic")

    # Mock the database query and delete operation to raise an exception
    with (
        mock.patch.object(
            Topic, "get_or_none", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_get,
        mock.patch.object(
            mock_topic, "delete", new=mock.AsyncMock(side_effect=delete_error)
        ) as mock_delete,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await delete_topic(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == delete_error
        mock_get.assert_called_once_with(id=test_id)
        mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_topic_cascading_deletion(mock_topic) -> None:
    # Arrange
    test_id = mock_topic.id

    # Create mock related objects that should be deleted
    mock_topic.topic_tags = [mock.MagicMock() for _ in range(3)]
    mock_topic.posts = [mock.MagicMock() for _ in range(2)]

    # Mock the database query - RULE #10 compliance: only operates on Topic model
    with (
        mock.patch.object(
            Topic, "get_or_none", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_get,
        mock.patch.object(mock_topic, "delete", new=mock.AsyncMock()) as mock_delete,
    ):
        # Act
        result = await delete_topic(test_id)

        # Assert
        assert result is True

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_delete.assert_called_once()

        # Note: We don't need to explicitly test that related objects are deleted
        # since Tortoise ORM handles cascading deletions automatically based on
        # the model relationships. The delete() method on the topic will trigger
        # the cascading deletions.
