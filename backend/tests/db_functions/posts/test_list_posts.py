# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.post import Post
from backend.db_functions.posts.list_posts import list_posts
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse


@pytest.fixture
def mock_posts() -> list[mock.MagicMock]:
    posts = []
    for i in range(3):
        post = mock.MagicMock(spec=Post)
        post.id = uuid.uuid4()
        post.content = f"Test Post Content {i}"
        post.author_id = uuid.uuid4()
        post.topic_id = uuid.uuid4()
        post.parent_post_id = None
        post.created_at = mock.MagicMock()
        post.updated_at = mock.MagicMock()
        posts.append(post)
    return posts


@pytest.fixture
def mock_post_responses(mock_posts) -> list[PostResponse]:
    return [mock.MagicMock(spec=PostResponse) for _ in mock_posts]


@pytest.mark.asyncio
async def test_list_posts_success(mock_posts, mock_post_responses) -> None:
    # Arrange
    skip = 0
    limit = 20
    expected_count = len(mock_posts)

    # Mock the database query - RULE #10 compliance: only operates on Post model
    with (
        mock.patch.object(Post, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
        mock.patch.object(
            mock_all.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=mock_posts),
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.posts.list_posts.post_to_schema",
            new=mock.AsyncMock(side_effect=mock_post_responses),
        ) as mock_converter,
    ):
        # Act
        result = await list_posts(skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert isinstance(result, PostList)
        assert result.count == expected_count
        assert len(result.posts) == expected_count
        assert result.posts == mock_post_responses

        # Verify function calls
        mock_all.assert_called_once()
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)
        assert mock_converter.call_count == expected_count


@pytest.mark.asyncio
async def test_list_posts_with_topic_filter(mock_posts, mock_post_responses) -> None:
    # Arrange
    skip = 0
    limit = 20
    topic_id = uuid.uuid4()
    expected_count = len(mock_posts)

    # Mock the database query
    with (
        mock.patch.object(Post, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
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
            new=mock.AsyncMock(return_value=mock_posts),
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.posts.list_posts.post_to_schema",
            new=mock.AsyncMock(side_effect=mock_post_responses),
        ) as mock_converter,
    ):
        # Act
        result = await list_posts(skip=skip, limit=limit, topic_id=topic_id)

        # Assert
        assert result is not None
        assert isinstance(result, PostList)
        assert result.count == expected_count
        assert len(result.posts) == expected_count
        assert result.posts == mock_post_responses

        # Verify function calls
        mock_all.assert_called_once()
        mock_filter.assert_called_once_with(topic_id=topic_id)
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)
        assert mock_converter.call_count == expected_count


@pytest.mark.asyncio
async def test_list_posts_with_author_filter(mock_posts, mock_post_responses) -> None:
    # Arrange
    skip = 0
    limit = 20
    author_id = uuid.uuid4()
    expected_count = len(mock_posts)

    # Mock the database query
    with (
        mock.patch.object(Post, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
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
            new=mock.AsyncMock(return_value=mock_posts),
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.posts.list_posts.post_to_schema",
            new=mock.AsyncMock(side_effect=mock_post_responses),
        ) as mock_converter,
    ):
        # Act
        result = await list_posts(skip=skip, limit=limit, author_id=author_id)

        # Assert
        assert result is not None
        assert isinstance(result, PostList)
        assert result.count == expected_count
        assert len(result.posts) == expected_count
        assert result.posts == mock_post_responses

        # Verify function calls
        mock_all.assert_called_once()
        mock_filter.assert_called_once_with(author_id=author_id)
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)
        assert mock_converter.call_count == expected_count


@pytest.mark.asyncio
async def test_list_posts_with_multiple_filters(
    mock_posts, mock_post_responses
) -> None:
    # Arrange
    skip = 0
    limit = 20
    topic_id = uuid.uuid4()
    author_id = uuid.uuid4()
    expected_count = len(mock_posts)

    # Mock the database query
    with (
        mock.patch.object(Post, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value, "filter", return_value=mock.MagicMock()
        ) as mock_filter_topic,
        mock.patch.object(
            mock_filter_topic.return_value, "filter", return_value=mock.MagicMock()
        ) as mock_filter_author,
        mock.patch.object(
            mock_filter_author.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
        mock.patch.object(
            mock_filter_author.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=mock_posts),
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.posts.list_posts.post_to_schema",
            new=mock.AsyncMock(side_effect=mock_post_responses),
        ) as mock_converter,
    ):
        # Act
        result = await list_posts(
            skip=skip, limit=limit, topic_id=topic_id, author_id=author_id
        )

        # Assert
        assert result is not None
        assert isinstance(result, PostList)
        assert result.count == expected_count
        assert len(result.posts) == expected_count
        assert result.posts == mock_post_responses

        # Verify function calls
        mock_all.assert_called_once()
        mock_filter_topic.assert_called_once_with(topic_id=topic_id)
        mock_filter_author.assert_called_once_with(author_id=author_id)
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)
        assert mock_converter.call_count == expected_count


@pytest.mark.asyncio
async def test_list_posts_empty_results() -> None:
    # Arrange
    skip = 0
    limit = 20
    expected_count = 0
    empty_posts = []

    # Mock the database query
    with (
        mock.patch.object(Post, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
        mock.patch.object(
            mock_all.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=empty_posts),
        ) as mock_limit,
    ):
        # Act
        result = await list_posts(skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert isinstance(result, PostList)
        assert result.count == expected_count
        assert len(result.posts) == expected_count

        # Verify function calls
        mock_all.assert_called_once()
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)


@pytest.mark.asyncio
async def test_list_posts_database_error() -> None:
    # Arrange
    skip = 0
    limit = 20
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Post, "all", new=mock.MagicMock(side_effect=db_error)
    ) as mock_all:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await list_posts(skip=skip, limit=limit)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_all.assert_called_once()
