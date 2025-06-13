# Standard library imports
from typing import List
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.expressions import Q

# Project-specific imports
from backend.db.models.pending_post import PendingPost
from backend.db_functions.pending_posts.list_pending_posts import list_pending_posts
from backend.schemas.pending_post import PendingPostList
from backend.schemas.pending_post import PendingPostResponse


@pytest.fixture
def mock_pending_post_response() -> mock.MagicMock:
    """Create a mock pending post response for testing."""
    response = mock.MagicMock(spec=PendingPostResponse)
    response.id = uuid.uuid4()
    response.content = "Test Pending Post Content"
    response.author_id = uuid.uuid4()
    response.topic_id = uuid.uuid4()
    return response


@pytest.fixture
def mock_pending_posts(count: int = 5) -> List[mock.MagicMock]:
    """Create a list of mock pending posts for testing."""
    pending_posts = []
    for i in range(count):
        post = mock.MagicMock(spec=PendingPost)
        post.id = uuid.uuid4()
        post.content = f"Test Pending Post Content {i + 1}"
        post.author_id = uuid.uuid4()
        post.topic_id = uuid.uuid4()
        post.parent_post_id = None
        post.created_at = mock.MagicMock()
        post.updated_at = mock.MagicMock()
        pending_posts.append(post)
    return pending_posts


@pytest.mark.asyncio
async def test_list_pending_posts_no_filters(
    mock_pending_posts, mock_pending_post_response
):
    """Test listing pending posts with no filters."""
    # Arrange
    limit = 10
    offset = 0
    total_count = len(mock_pending_posts)

    # Mock dependencies
    with (
        mock.patch.object(
            PendingPost, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.pending_posts.list_pending_posts.pending_post_to_schema",
            new=mock.AsyncMock(return_value=mock_pending_post_response),
        ) as mock_converter,
    ):
        # Configure mock filter chain
        mock_filter.return_value.count = mock.AsyncMock(return_value=total_count)
        mock_filter.return_value.limit = mock.MagicMock(
            return_value=mock_filter.return_value
        )
        mock_filter.return_value.offset = mock.MagicMock(
            return_value=mock_filter.return_value
        )
        mock_filter.return_value.order_by = mock.AsyncMock(
            return_value=mock_pending_posts
        )

        # Act
        result = await list_pending_posts(limit=limit, offset=offset)

        # Assert
        assert isinstance(result, PendingPostList)
        assert result.count == total_count
        assert len(result.pending_posts) == len(mock_pending_posts)

        # Verify function calls
        mock_filter.assert_called_with(Q())
        mock_filter.return_value.limit.assert_called_once_with(limit)
        mock_filter.return_value.offset.assert_called_once_with(offset)
        mock_filter.return_value.order_by.assert_called_once_with("-created_at")

        # Verify converter called for each post
        assert mock_converter.call_count == len(mock_pending_posts)


@pytest.mark.asyncio
async def test_list_pending_posts_pagination(
    mock_pending_posts, mock_pending_post_response
):
    """Test listing pending posts with pagination."""
    # Arrange
    limit = 3
    offset = 2
    total_count = 10  # Total count is higher than the returned posts

    # Mock dependencies
    with (
        mock.patch.object(
            PendingPost, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.pending_posts.list_pending_posts.pending_post_to_schema",
            new=mock.AsyncMock(return_value=mock_pending_post_response),
        ),
    ):
        # Configure mock filter chain
        mock_filter.return_value.count = mock.AsyncMock(return_value=total_count)
        mock_filter.return_value.limit = mock.MagicMock(
            return_value=mock_filter.return_value
        )
        mock_filter.return_value.offset = mock.MagicMock(
            return_value=mock_filter.return_value
        )
        mock_filter.return_value.order_by = mock.AsyncMock(
            return_value=mock_pending_posts[:limit]
        )

        # Act
        result = await list_pending_posts(limit=limit, offset=offset)

        # Assert
        assert isinstance(result, PendingPostList)
        assert result.count == total_count  # Total count should reflect all posts
        assert len(result.pending_posts) == limit  # But only limited number returned

        # Verify pagination parameters
        mock_filter.return_value.limit.assert_called_once_with(limit)
        mock_filter.return_value.offset.assert_called_once_with(offset)


@pytest.mark.asyncio
async def test_list_pending_posts_empty_results():
    """Test listing pending posts when no posts match the criteria."""
    # Arrange
    user_id = uuid.uuid4()
    limit = 10
    offset = 0

    # Mock dependencies
    with (
        mock.patch.object(
            PendingPost, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.pending_posts.list_pending_posts.pending_post_to_schema",
            new=mock.AsyncMock(),
        ) as mock_converter,
    ):
        # Configure mock filter chain to return empty list
        mock_filter.return_value.count = mock.AsyncMock(return_value=0)
        mock_filter.return_value.limit = mock.MagicMock(
            return_value=mock_filter.return_value
        )
        mock_filter.return_value.offset = mock.MagicMock(
            return_value=mock_filter.return_value
        )
        mock_filter.return_value.order_by = mock.AsyncMock(return_value=[])

        # Act
        result = await list_pending_posts(user_id=user_id, limit=limit, offset=offset)

        # Assert
        assert isinstance(result, PendingPostList)
        assert result.count == 0
        assert len(result.pending_posts) == 0

        # Verify converter was not called since there are no posts
        mock_converter.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_pending_posts_database_error():
    """Test handling database errors during listing."""
    # Arrange
    db_error = Exception("Database error")

    # Mock dependencies
    with (
        mock.patch.object(PendingPost, "filter", side_effect=db_error),
        pytest.raises(Exception) as exc_info,
    ):
        # Act
        await list_pending_posts()

    # Assert
    assert exc_info.value == db_error
