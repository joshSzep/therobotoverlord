# Standard library imports
from datetime import datetime
from typing import List
from typing import cast
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.topics.list_topic_posts import list_topic_posts
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse


@pytest.mark.asyncio
async def test_list_topic_posts_success():
    """Test successful listing of posts for a topic."""
    # Arrange
    topic_id = uuid.uuid4()

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Create mock posts
    mock_post1 = mock.MagicMock(spec=PostResponse)
    mock_post1.id = uuid.uuid4()
    mock_post1.title = "Test Post 1"
    mock_post1.content = "This is test post 1"
    mock_post1.parent_post_id = None  # Top-level post
    mock_post1.created_at = datetime(2025, 5, 25)
    mock_post1.updated_at = datetime(2025, 5, 25)

    mock_post2 = mock.MagicMock(spec=PostResponse)
    mock_post2.id = uuid.uuid4()
    mock_post2.title = "Test Post 2"
    mock_post2.content = "This is test post 2"
    mock_post2.parent_post_id = None  # Top-level post
    mock_post2.created_at = datetime(2025, 5, 26)
    mock_post2.updated_at = datetime(2025, 5, 26)

    # Create a reply post (should be filtered out)
    mock_reply = mock.MagicMock(spec=PostResponse)
    mock_reply.id = uuid.uuid4()
    mock_reply.title = "Reply Post"
    mock_reply.content = "This is a reply"
    mock_reply.parent_post_id = mock_post1.id  # Reply to post 1
    mock_reply.created_at = datetime(2025, 5, 27)
    mock_reply.updated_at = datetime(2025, 5, 27)

    # Create mock post list
    mock_posts = [mock_post1, mock_post2, mock_reply]
    # Cast mock_posts to the expected type
    posts_list = cast(List[PostResponse], mock_posts)
    mock_post_list = PostList(posts=posts_list, count=len(mock_posts))

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.list_topic_posts.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.list_topic_posts.list_posts",
            new=mock.AsyncMock(return_value=mock_post_list),
        ) as mock_list_posts,
    ):
        # Act
        result = await list_topic_posts(
            topic_id=topic_id,
            skip=0,
            limit=10,
        )

        # Assert
        assert isinstance(result, PostList)
        assert len(result.posts) == 2  # Only top-level posts
        assert result.count == 2

        # Verify the posts are the top-level ones
        assert all(post.parent_post_id is None for post in result.posts)
        assert mock_post1 in result.posts
        assert mock_post2 in result.posts
        assert mock_reply not in result.posts

        # Verify function calls
        mock_list_posts.assert_called_once_with(
            skip=0,
            limit=10,
            topic_id=topic_id,
        )


@pytest.mark.asyncio
async def test_list_topic_posts_topic_not_found():
    """Test listing posts with non-existent topic."""
    # Arrange
    topic_id = uuid.uuid4()

    # Mock dependencies - simulate topic not found
    with mock.patch(
        "backend.routes.topics.list_topic_posts.get_topic_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await list_topic_posts(
                topic_id=topic_id,
                skip=0,
                limit=10,
            )

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Topic not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_list_topic_posts_with_pagination():
    """Test listing posts with pagination."""
    # Arrange
    topic_id = uuid.uuid4()

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Create mock posts (all top-level)
    mock_posts = []
    for i in range(5):
        mock_post = mock.MagicMock(spec=PostResponse)
        mock_post.id = uuid.uuid4()
        mock_post.title = f"Test Post {i + 1}"
        mock_post.content = f"This is test post {i + 1}"
        mock_post.parent_post_id = None
        mock_post.created_at = datetime(2025, 5, 25)
        mock_post.updated_at = datetime(2025, 5, 25)
        mock_posts.append(mock_post)

    # Cast mock_posts to the expected type
    posts_list = cast(List[PostResponse], mock_posts)
    mock_post_list = PostList(posts=posts_list, count=len(mock_posts))

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.list_topic_posts.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.list_topic_posts.list_posts",
            new=mock.AsyncMock(return_value=mock_post_list),
        ) as mock_list_posts,
    ):
        # Act
        result = await list_topic_posts(
            topic_id=topic_id,
            skip=2,
            limit=3,
        )

        # Assert
        assert isinstance(result, PostList)
        assert len(result.posts) == 5  # All posts are top-level
        assert result.count == 5

        # Verify function calls with correct pagination parameters
        mock_list_posts.assert_called_once_with(
            skip=2,
            limit=3,
            topic_id=topic_id,
        )
