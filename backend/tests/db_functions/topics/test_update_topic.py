# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic import Topic
from backend.db_functions.topics.update_topic import update_topic
from backend.schemas.topic import TopicResponse


@pytest.fixture
def mock_topic() -> mock.MagicMock:
    topic = mock.MagicMock(spec=Topic)
    topic.id = uuid.uuid4()
    topic.title = "Original Title"
    topic.description = "Original Description"
    topic.author_id = uuid.uuid4()
    topic.created_at = mock.MagicMock()
    topic.updated_at = mock.MagicMock()
    return topic


@pytest.fixture
def mock_topic_response(mock_topic) -> TopicResponse:
    return mock.MagicMock(spec=TopicResponse)


@pytest.mark.asyncio
async def test_update_topic_success(mock_topic, mock_topic_response) -> None:
    # Arrange
    test_id = mock_topic.id
    new_title = "Updated Title"
    new_description = "Updated Description"

    # Mock the database query - RULE #10 compliance: only operates on Topic model
    with (
        mock.patch.object(
            Topic, "get_or_none", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_get,
        mock.patch.object(mock_topic, "save", new=mock.AsyncMock()) as mock_save,
        mock.patch(
            "backend.db_functions.topics.update_topic.topic_to_schema",
            new=mock.AsyncMock(return_value=mock_topic_response),
        ) as mock_converter,
    ):
        # Act
        result = await update_topic(
            topic_id=test_id,
            title=new_title,
            description=new_description,
        )

        # Assert
        assert result is not None
        assert result == mock_topic_response
        assert mock_topic.title == new_title
        assert mock_topic.description == new_description

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_save.assert_called_once()
        mock_converter.assert_called_once_with(mock_topic)


@pytest.mark.asyncio
async def test_update_topic_partial_update(mock_topic, mock_topic_response) -> None:
    # Arrange
    test_id = mock_topic.id
    original_title = mock_topic.title
    new_description = "Updated Description"

    # Mock the database query - RULE #10 compliance: only operates on Topic model
    with (
        mock.patch.object(
            Topic, "get_or_none", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_get,
        mock.patch.object(mock_topic, "save", new=mock.AsyncMock()) as mock_save,
        mock.patch(
            "backend.db_functions.topics.update_topic.topic_to_schema",
            new=mock.AsyncMock(return_value=mock_topic_response),
        ) as mock_converter,
    ):
        # Act - Only update description
        result = await update_topic(
            topic_id=test_id,
            description=new_description,
        )

        # Assert
        assert result is not None
        assert result == mock_topic_response
        assert mock_topic.title == original_title  # Title should remain unchanged
        assert mock_topic.description == new_description

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_save.assert_called_once()
        mock_converter.assert_called_once_with(mock_topic)


@pytest.mark.asyncio
async def test_update_topic_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()
    new_title = "Updated Title"
    new_description = "Updated Description"

    # Mock the database query
    with mock.patch.object(
        Topic, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await update_topic(
            topic_id=test_id,
            title=new_title,
            description=new_description,
        )

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_update_topic_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    new_title = "Updated Title"
    new_description = "Updated Description"
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Topic, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await update_topic(
                topic_id=test_id,
                title=new_title,
                description=new_description,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_update_topic_save_error(mock_topic) -> None:
    # Arrange
    test_id = mock_topic.id
    new_title = "Updated Title"
    save_error = IntegrityError("Error saving topic")

    # Mock the database query and save operation to raise an exception
    with (
        mock.patch.object(
            Topic, "get_or_none", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_get,
        mock.patch.object(
            mock_topic, "save", new=mock.AsyncMock(side_effect=save_error)
        ) as mock_save,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await update_topic(
                topic_id=test_id,
                title=new_title,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_get.assert_called_once_with(id=test_id)
        mock_save.assert_called_once()
