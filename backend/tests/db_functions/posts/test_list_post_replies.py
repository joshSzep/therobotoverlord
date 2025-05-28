# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.post import Post
from backend.db_functions.posts.list_post_replies import list_post_replies
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse


@pytest.fixture
def mock_reply_posts() -> list[mock.MagicMock]:
    posts = []
    for i in range(3):
        post = mock.MagicMock(spec=Post)
        post.id = uuid.uuid4()
        post.content = f"Test Reply Content {i}"
        post.author_id = uuid.uuid4()
        post.topic_id = uuid.uuid4()
        post.parent_post_id = uuid.uuid4()  # Same parent post ID
        post.created_at = mock.MagicMock()
        post.updated_at = mock.MagicMock()
        posts.append(post)
    return posts


@pytest.fixture
def mock_post_responses(mock_reply_posts) -> list[PostResponse]:
    return [mock.MagicMock(spec=PostResponse) for _ in mock_reply_posts]


@pytest.mark.asyncio
async def test_list_post_replies_success(mock_reply_posts, mock_post_responses) -> None:
    # Arrange
    parent_post_id = uuid.uuid4()
    skip = 0
    limit = 20
    expected_count = len(mock_reply_posts)

    # Mock the database query - RULE #10 compliance: only operates on Post model
    with (
        mock.patch.object(Post, "filter", return_value=mock.MagicMock()) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
        mock.patch.object(
            mock_filter.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=mock_reply_posts),
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.posts.list_post_replies.post_to_schema",
            new=mock.AsyncMock(side_effect=mock_post_responses),
        ) as mock_converter,
    ):
        # Act
        result = await list_post_replies(post_id=parent_post_id, skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert isinstance(result, PostList)
        assert result.count == expected_count
        assert len(result.posts) == expected_count
        assert result.posts == mock_post_responses

        # Verify function calls
        mock_filter.assert_called_once_with(parent_post_id=parent_post_id)
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)
        assert mock_converter.call_count == expected_count


@pytest.mark.asyncio
async def test_list_post_replies_with_pagination(
    mock_reply_posts, mock_post_responses
) -> None:
    # Arrange
    parent_post_id = uuid.uuid4()
    skip = 5
    limit = 10
    expected_count = len(mock_reply_posts)

    # Mock the database query
    with (
        mock.patch.object(Post, "filter", return_value=mock.MagicMock()) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
        mock.patch.object(
            mock_filter.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=mock_reply_posts),
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.posts.list_post_replies.post_to_schema",
            new=mock.AsyncMock(side_effect=mock_post_responses),
        ) as mock_converter,
    ):
        # Act
        result = await list_post_replies(post_id=parent_post_id, skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert isinstance(result, PostList)
        assert result.count == expected_count
        assert len(result.posts) == expected_count
        assert result.posts == mock_post_responses

        # Verify function calls
        mock_filter.assert_called_once_with(parent_post_id=parent_post_id)
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)
        assert mock_converter.call_count == expected_count


@pytest.mark.asyncio
async def test_list_post_replies_empty_results() -> None:
    # Arrange
    parent_post_id = uuid.uuid4()
    skip = 0
    limit = 20
    expected_count = 0
    empty_posts = []

    # Mock the database query
    with (
        mock.patch.object(Post, "filter", return_value=mock.MagicMock()) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
        mock.patch.object(
            mock_filter.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=empty_posts),
        ) as mock_limit,
    ):
        # Act
        result = await list_post_replies(post_id=parent_post_id, skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert isinstance(result, PostList)
        assert result.count == expected_count
        assert len(result.posts) == expected_count

        # Verify function calls
        mock_filter.assert_called_once_with(parent_post_id=parent_post_id)
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)


@pytest.mark.asyncio
async def test_list_post_replies_database_error() -> None:
    # Arrange
    parent_post_id = uuid.uuid4()
    skip = 0
    limit = 20
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Post, "filter", new=mock.MagicMock(side_effect=db_error)
    ) as mock_filter:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await list_post_replies(post_id=parent_post_id, skip=skip, limit=limit)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(parent_post_id=parent_post_id)
