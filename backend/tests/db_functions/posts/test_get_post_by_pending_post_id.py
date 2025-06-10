# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import DoesNotExist

# Project-specific imports
from backend.db.models.post import Post
from backend.db_functions.posts.get_post_by_pending_post_id import (
    get_post_by_pending_post_id,
)
from backend.schemas.post import PostResponse


@pytest.fixture
def mock_post() -> mock.MagicMock:
    """Returns a mock Post object."""
    post = mock.MagicMock(spec=Post)
    post.id = uuid.uuid4()
    post.content = "This is an approved post."
    post.author_id = uuid.uuid4()
    post.topic_id = uuid.uuid4()
    return post


@pytest.fixture
def mock_post_response() -> mock.MagicMock:
    """Returns a mock PostResponse object."""
    return mock.MagicMock(spec=PostResponse)


@pytest.fixture
def mock_approval_event() -> mock.MagicMock:
    """Returns a mock approval event."""
    event = mock.MagicMock()
    event.metadata = {"approved_post_id": str(uuid.uuid4())}
    return event


@pytest.mark.asyncio
async def test_get_post_by_pending_post_id_success(
    mock_post, mock_post_response, mock_approval_event
) -> None:
    """
    Test get_post_by_pending_post_id successfully finds and returns a post.
    """
    # Arrange
    pending_post_id = uuid.uuid4()
    approved_post_id = uuid.UUID(mock_approval_event.metadata["approved_post_id"])

    # Mock the dependencies
    with (
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.get_post_approval_event",
            new=mock.AsyncMock(return_value=mock_approval_event),
        ) as mock_get_event,
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_get_post,
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.post_to_schema",
            new=mock.AsyncMock(return_value=mock_post_response),
        ) as mock_converter,
    ):
        # Act
        result = await get_post_by_pending_post_id(pending_post_id)

        # Assert
        assert result is not None
        assert result == mock_post_response
        mock_get_event.assert_called_once_with(pending_post_id)
        mock_get_post.assert_called_once_with(id=approved_post_id)
        mock_converter.assert_called_once_with(mock_post)


@pytest.mark.asyncio
async def test_get_post_by_pending_post_id_no_event() -> None:
    """
    Test get_post_by_pending_post_id returns None when no approval event is found.
    """
    # Arrange
    pending_post_id = uuid.uuid4()

    # Mock the dependencies
    with (
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.get_post_approval_event",
            new=mock.AsyncMock(return_value=None),
        ) as mock_get_event,
        mock.patch.object(Post, "get_or_none") as mock_get_post,
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.post_to_schema"
        ) as mock_converter,
    ):
        # Act
        result = await get_post_by_pending_post_id(pending_post_id)

        # Assert
        assert result is None
        mock_get_event.assert_called_once_with(pending_post_id)
        mock_get_post.assert_not_called()
        mock_converter.assert_not_called()


@pytest.mark.asyncio
async def test_get_post_by_pending_post_id_event_without_metadata() -> None:
    """
    Test get_post_by_pending_post_id returns None when the event has no metadata.
    """
    # Arrange
    pending_post_id = uuid.uuid4()
    event = mock.MagicMock()
    event.metadata = None

    # Mock the dependencies
    with (
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.get_post_approval_event",
            new=mock.AsyncMock(return_value=event),
        ) as mock_get_event,
        mock.patch.object(Post, "get_or_none") as mock_get_post,
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.post_to_schema"
        ) as mock_converter,
    ):
        # Act
        result = await get_post_by_pending_post_id(pending_post_id)

        # Assert
        assert result is None
        mock_get_event.assert_called_once_with(pending_post_id)
        mock_get_post.assert_not_called()
        mock_converter.assert_not_called()


@pytest.mark.asyncio
async def test_get_post_by_pending_post_id_event_without_approved_post_id() -> None:
    """
    Test get_post_by_pending_post_id returns None when the event metadata doesn't have
    approved_post_id.
    """
    # Arrange
    pending_post_id = uuid.uuid4()
    event = mock.MagicMock()
    event.metadata = {"some_other_key": "value"}

    # Mock the dependencies
    with (
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.get_post_approval_event",
            new=mock.AsyncMock(return_value=event),
        ) as mock_get_event,
        mock.patch.object(Post, "get_or_none") as mock_get_post,
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.post_to_schema"
        ) as mock_converter,
    ):
        # Act
        result = await get_post_by_pending_post_id(pending_post_id)

        # Assert
        assert result is None
        mock_get_event.assert_called_once_with(pending_post_id)
        mock_get_post.assert_not_called()
        mock_converter.assert_not_called()


@pytest.mark.asyncio
async def test_get_post_by_pending_post_id_post_not_found(mock_approval_event) -> None:
    """
    Test get_post_by_pending_post_id returns None when the approved post is not found.
    """
    # Arrange
    pending_post_id = uuid.uuid4()
    approved_post_id = uuid.UUID(mock_approval_event.metadata["approved_post_id"])

    # Mock the dependencies
    with (
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.get_post_approval_event",
            new=mock.AsyncMock(return_value=mock_approval_event),
        ) as mock_get_event,
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=None)
        ) as mock_get_post,
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.post_to_schema"
        ) as mock_converter,
    ):
        # Act
        result = await get_post_by_pending_post_id(pending_post_id)

        # Assert
        assert result is None
        mock_get_event.assert_called_once_with(pending_post_id)
        mock_get_post.assert_called_once_with(id=approved_post_id)
        mock_converter.assert_not_called()


@pytest.mark.asyncio
async def test_get_post_by_pending_post_id_database_error() -> None:
    """
    Test get_post_by_pending_post_id handles database errors gracefully.
    """
    # Arrange
    pending_post_id = uuid.uuid4()
    db_error = DoesNotExist("Database error")

    # Mock the dependencies
    with (
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.get_post_approval_event",
            new=mock.AsyncMock(side_effect=db_error),
        ) as mock_get_event,
        mock.patch(
            "backend.db_functions.posts.get_post_by_pending_post_id.logger.error"
        ) as mock_logger_error,
    ):
        # Act
        result = await get_post_by_pending_post_id(pending_post_id)

        # Assert
        assert result is None
        mock_get_event.assert_called_once_with(pending_post_id)
        mock_logger_error.assert_called_once_with(
            f"Error finding post by pending post ID: {db_error}"
        )
