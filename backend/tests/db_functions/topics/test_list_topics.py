# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.topic import Topic
from backend.db_functions.topics.list_topics import list_topics
from backend.schemas.topic import TopicList
from backend.schemas.topic import TopicResponse


@pytest.fixture
def mock_topics() -> list[mock.MagicMock]:
    topics = []
    for i in range(3):
        topic = mock.MagicMock(spec=Topic)
        topic.id = uuid.uuid4()
        topic.title = f"Test Topic {i}"
        topic.description = f"Test Description {i}"
        topic.author_id = uuid.uuid4()
        topic.created_at = mock.MagicMock()
        topic.updated_at = mock.MagicMock()
        topics.append(topic)
    return topics


@pytest.fixture
def mock_topic_responses(mock_topics) -> list[TopicResponse]:
    return [mock.MagicMock(spec=TopicResponse) for _ in mock_topics]


@pytest.fixture
def mock_topic_list(mock_topic_responses) -> TopicList:
    return TopicList(topics=mock_topic_responses, count=len(mock_topic_responses))


@pytest.mark.asyncio
async def test_list_topics_success(
    mock_topics, mock_topic_responses, mock_topic_list
) -> None:
    # Arrange
    skip = 0
    limit = 20
    count = len(mock_topics)

    # Mock the database query - RULE #10 compliance: only operates on Topic model
    with (
        mock.patch.object(Topic, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value, "count", new=mock.AsyncMock(return_value=count)
        ) as mock_count,
        mock.patch.object(
            mock_all.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=mock_topics),
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.topics.list_topics.topic_to_schema",
            new=mock.AsyncMock(side_effect=mock_topic_responses),
        ) as mock_converter,
    ):
        # Act
        result = await list_topics(skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert result.count == count
        assert len(result.topics) == len(mock_topic_responses)

        # Verify function calls
        mock_all.assert_called_once()
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)
        assert mock_converter.call_count == len(mock_topics)


@pytest.mark.asyncio
async def test_list_topics_pagination() -> None:
    # Arrange
    skip = 10
    limit = 5
    topics = [mock.MagicMock(spec=Topic) for _ in range(5)]
    count = 20  # Total count of topics

    # Mock the database query
    with (
        mock.patch.object(Topic, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value, "count", new=mock.AsyncMock(return_value=count)
        ),
        mock.patch.object(
            mock_all.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value, "limit", new=mock.AsyncMock(return_value=topics)
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.topics.list_topics.topic_to_schema",
            new=mock.AsyncMock(return_value=mock.MagicMock(spec=TopicResponse)),
        ),
    ):
        # Act
        result = await list_topics(skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert result.count == count
        assert len(result.topics) == len(topics)

        # Verify pagination parameters are used correctly
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)


@pytest.mark.asyncio
async def test_list_topics_empty_results() -> None:
    # Arrange
    skip = 0
    limit = 20
    topics = []
    count = 0

    # Mock the database query
    with (
        mock.patch.object(Topic, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value, "count", new=mock.AsyncMock(return_value=count)
        ),
        mock.patch.object(
            mock_all.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value, "limit", new=mock.AsyncMock(return_value=topics)
        ),
    ):
        # Act
        result = await list_topics(skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert result.count == 0
        assert len(result.topics) == 0


@pytest.mark.asyncio
async def test_list_topics_database_error() -> None:
    # Arrange
    skip = 0
    limit = 20
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(Topic, "all", side_effect=db_error) as mock_all:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await list_topics(skip=skip, limit=limit)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_all.assert_called_once()
