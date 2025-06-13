# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.post import Post
from backend.db_functions.posts.find_post_by_content import find_post_by_content
from backend.schemas.post import PostResponse


@pytest.fixture
def mock_post() -> mock.MagicMock:
    """Returns a mock Post object."""
    post = mock.MagicMock(spec=Post)
    post.id = uuid.uuid4()
    post.content = "This is the exact content of the post."
    post.author_id = uuid.uuid4()
    post.topic_id = uuid.uuid4()
    return post


@pytest.fixture
def mock_post_response() -> mock.MagicMock:
    """Returns a mock PostResponse object."""
    return mock.MagicMock(spec=PostResponse)


@pytest.mark.asyncio
async def test_find_post_by_content_success(mock_post, mock_post_response) -> None:
    """
    Test find_post_by_content successfully finds and returns a post.
    """
    # Arrange
    content = mock_post.content
    topic_id = mock_post.topic_id
    author_id = mock_post.author_id

    # Mock the database query
    with (
        mock.patch.object(Post, "filter", return_value=mock.MagicMock()) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "first",
            new=mock.AsyncMock(return_value=mock_post),
        ) as mock_first,
        mock.patch(
            "backend.db_functions.posts.find_post_by_content.post_to_schema",
            new=mock.AsyncMock(return_value=mock_post_response),
        ) as mock_converter,
    ):
        # Act
        result = await find_post_by_content(content, topic_id, author_id)

        # Assert
        assert result is not None
        assert result == mock_post_response
        mock_filter.assert_called_once_with(
            content=content, topic_id=topic_id, author_id=author_id
        )
        mock_first.assert_called_once()
        mock_converter.assert_called_once_with(mock_post)


@pytest.mark.asyncio
async def test_find_post_by_content_not_found() -> None:
    """
    Test find_post_by_content returns None when no post is found.
    """
    # Arrange
    content = "Some content that does not exist"
    topic_id = uuid.uuid4()
    author_id = uuid.uuid4()

    # Mock the database query to return no post
    with (
        mock.patch.object(Post, "filter", return_value=mock.MagicMock()) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "first",
            new=mock.AsyncMock(return_value=None),
        ) as mock_first,
        mock.patch(
            "backend.db_functions.posts.find_post_by_content.post_to_schema"
        ) as mock_converter,
    ):
        # Act
        result = await find_post_by_content(content, topic_id, author_id)

        # Assert
        assert result is None
        mock_filter.assert_called_once_with(
            content=content, topic_id=topic_id, author_id=author_id
        )
        mock_first.assert_called_once()
        mock_converter.assert_not_called()


@pytest.mark.asyncio
async def test_find_post_by_content_database_error() -> None:
    """
    Test find_post_by_content handles database errors gracefully.
    """
    # Arrange
    content = "Some content"
    topic_id = uuid.uuid4()
    author_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with (
        mock.patch.object(
            Post, "filter", new=mock.MagicMock(side_effect=db_error)
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.posts.find_post_by_content.logger.error"
        ) as mock_logger_error,
    ):
        # Act
        result = await find_post_by_content(content, topic_id, author_id)

        # Assert
        assert result is None
        mock_filter.assert_called_once_with(
            content=content, topic_id=topic_id, author_id=author_id
        )
        mock_logger_error.assert_called_once_with(
            f"Error finding post by content: {str(db_error)}"
        )


@pytest.mark.asyncio
async def test_find_post_by_content_converter_error(mock_post) -> None:
    """
    Test find_post_by_content handles schema conversion errors gracefully.
    """
    # Arrange
    content = mock_post.content
    topic_id = mock_post.topic_id
    author_id = mock_post.author_id
    converter_error = ValueError("Schema conversion error")

    # Mock the database query but make converter fail
    with (
        mock.patch.object(Post, "filter", return_value=mock.MagicMock()) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "first",
            new=mock.AsyncMock(return_value=mock_post),
        ) as mock_first,
        mock.patch(
            "backend.db_functions.posts.find_post_by_content.post_to_schema",
            new=mock.AsyncMock(side_effect=converter_error),
        ) as mock_converter,
        mock.patch(
            "backend.db_functions.posts.find_post_by_content.logger.error"
        ) as mock_logger_error,
    ):
        # Act
        result = await find_post_by_content(content, topic_id, author_id)

        # Assert
        assert result is None
        mock_filter.assert_called_once_with(
            content=content, topic_id=topic_id, author_id=author_id
        )
        mock_first.assert_called_once()
        mock_converter.assert_called_once_with(mock_post)
        mock_logger_error.assert_called_once_with(
            f"Error finding post by content: {str(converter_error)}"
        )
