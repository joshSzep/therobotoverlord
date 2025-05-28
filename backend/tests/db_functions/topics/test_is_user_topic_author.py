# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic import Topic
from backend.db.models.user import User
from backend.db_functions.topics.is_user_topic_author import is_user_topic_author


@pytest.fixture
def mock_topic() -> mock.MagicMock:
    topic = mock.MagicMock(spec=Topic)
    topic.id = uuid.uuid4()
    topic.title = "Test Topic"
    topic.description = "Test Description"
    return topic


@pytest.fixture
def mock_author() -> mock.MagicMock:
    author = mock.MagicMock(spec=User)
    author.id = uuid.uuid4()
    return author


@pytest.mark.asyncio
async def test_is_user_topic_author_when_user_is_author(
    mock_topic, mock_author
) -> None:
    # Arrange
    topic_id = mock_topic.id
    user_id = mock_author.id
    mock_topic.author = mock_author

    # Mock the database query - RULE #10 compliance: only operates on Topic model
    with (
        mock.patch.object(
            Topic, "get_or_none", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_get,
        mock.patch.object(
            mock_topic, "fetch_related", new=mock.AsyncMock()
        ) as mock_fetch,
    ):
        # Act
        result = await is_user_topic_author(topic_id=topic_id, user_id=user_id)

        # Assert
        assert result is True

        # Verify function calls
        mock_get.assert_called_once_with(id=topic_id)
        mock_fetch.assert_called_once_with("author")


@pytest.mark.asyncio
async def test_is_user_topic_author_when_user_is_not_author(
    mock_topic, mock_author
) -> None:
    # Arrange
    topic_id = mock_topic.id
    user_id = uuid.uuid4()  # Different user ID
    mock_topic.author = mock_author

    # Mock the database query
    with (
        mock.patch.object(
            Topic, "get_or_none", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_get,
        mock.patch.object(
            mock_topic, "fetch_related", new=mock.AsyncMock()
        ) as mock_fetch,
    ):
        # Act
        result = await is_user_topic_author(topic_id=topic_id, user_id=user_id)

        # Assert
        assert result is False

        # Verify function calls
        mock_get.assert_called_once_with(id=topic_id)
        mock_fetch.assert_called_once_with("author")


@pytest.mark.asyncio
async def test_is_user_topic_author_when_topic_doesnt_exist() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Mock the database query
    with mock.patch.object(
        Topic, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await is_user_topic_author(topic_id=topic_id, user_id=user_id)

        # Assert
        assert result is False

        # Verify function calls
        mock_get.assert_called_once_with(id=topic_id)


@pytest.mark.asyncio
async def test_is_user_topic_author_database_error() -> None:
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Topic, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await is_user_topic_author(topic_id=topic_id, user_id=user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=topic_id)


@pytest.mark.asyncio
async def test_is_user_topic_author_fetch_related_error(mock_topic) -> None:
    # Arrange
    topic_id = mock_topic.id
    user_id = uuid.uuid4()
    fetch_error = IntegrityError("Error fetching related data")

    # Mock the database query and fetch_related to raise an exception
    with (
        mock.patch.object(
            Topic, "get_or_none", new=mock.AsyncMock(return_value=mock_topic)
        ) as mock_get,
        mock.patch.object(
            mock_topic, "fetch_related", new=mock.AsyncMock(side_effect=fetch_error)
        ) as mock_fetch,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await is_user_topic_author(topic_id=topic_id, user_id=user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == fetch_error
        mock_get.assert_called_once_with(id=topic_id)
        mock_fetch.assert_called_once_with("author")
