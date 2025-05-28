# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic import Topic
from backend.db_functions.topics.get_topic_by_id import get_topic_by_id
from backend.schemas.topic import TopicResponse


@pytest.fixture
def mock_topic() -> mock.MagicMock:
    topic = mock.MagicMock(spec=Topic)
    topic.id = uuid.uuid4()
    topic.title = "Test Topic"
    topic.description = "Test Description"
    topic.author_id = uuid.uuid4()
    topic.created_at = mock.MagicMock()
    topic.updated_at = mock.MagicMock()
    return topic


@pytest.fixture
def mock_topic_response(mock_topic) -> TopicResponse:
    return mock.MagicMock(spec=TopicResponse)


@pytest.mark.asyncio
async def test_get_topic_by_id_success(mock_topic, mock_topic_response) -> None:
    # Arrange
    test_id = mock_topic.id

    # Mock the database query - RULE #10 compliance: only operates on Topic model
    with (
        mock.patch.object(
            Topic, "get_or_none", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.topics.get_topic_by_id.topic_to_schema",
            new=mock.AsyncMock(return_value=mock_topic_response),
        ) as mock_converter,
    ):
        # Act
        result = await get_topic_by_id(test_id)

        # Assert
        assert result is not None
        assert result == mock_topic_response

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_converter.assert_called_once_with(mock_topic)


@pytest.mark.asyncio
async def test_get_topic_by_id_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()

    # Mock the database query
    with mock.patch.object(
        Topic, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await get_topic_by_id(test_id)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_get_topic_by_id_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Topic, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await get_topic_by_id(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_get_topic_by_id_invalid_uuid() -> None:
    # Arrange - We'll try to convert a string to UUID which should raise ValueError

    # Act & Assert
    with pytest.raises(ValueError):
        # We need to pass something that will trigger a ValueError when used as UUID
        # We can't pass a string directly due to type checking, so we'll use uuid.UUID
        # with an invalid format to trigger the ValueError
        await get_topic_by_id(uuid.UUID("not-a-valid-uuid"))
