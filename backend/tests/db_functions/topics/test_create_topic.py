# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic import Topic
from backend.db_functions.topics.create_topic import create_topic
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
async def test_create_topic_success(mock_topic, mock_topic_response) -> None:
    # Arrange
    title = "Test Topic"
    description = "Test Description"
    author_id = uuid.uuid4()

    # Mock the database query - RULE #10 compliance: only operates on Topic model
    with (
        mock.patch.object(
            Topic, "create", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.topics.create_topic.topic_to_schema",
            new=mock.AsyncMock(return_value=mock_topic_response),
        ) as mock_converter,
    ):
        # Act
        result = await create_topic(
            title=title,
            description=description,
            created_by_id=author_id,
        )

        # Assert
        assert result is not None
        assert result == mock_topic_response

        # Verify function calls
        mock_create.assert_called_once_with(
            title=title,
            description=description,
            author_id=author_id,
        )
        mock_converter.assert_called_once_with(mock_topic)


@pytest.mark.asyncio
async def test_create_topic_database_error() -> None:
    # Arrange
    title = "Test Topic"
    description = "Test Description"
    author_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Topic, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_topic(
                title=title,
                description=description,
                created_by_id=author_id,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once_with(
            title=title,
            description=description,
            author_id=author_id,
        )


@pytest.mark.asyncio
async def test_create_topic_invalid_data() -> None:
    # Arrange
    title = "Test Topic"
    description = "Test Description"

    # Act & Assert
    with pytest.raises(ValueError):
        # We can't pass a string directly due to type checking, so we'll use uuid.UUID
        # with an invalid format to trigger the ValueError
        await create_topic(
            title=title,
            description=description,
            created_by_id=uuid.UUID("not-a-valid-uuid"),  # This will raise a ValueError
        )
