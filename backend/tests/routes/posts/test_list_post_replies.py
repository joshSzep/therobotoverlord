from datetime import datetime
from unittest import mock
import uuid

from fastapi import HTTPException
import pytest

from backend.routes.auth.schemas import UserSchema
from backend.routes.posts.list_post_replies import list_post_replies
from backend.routes.posts.schemas import PostList


@pytest.mark.asyncio
async def test_list_post_replies_success():
    """Test successful listing of post replies."""
    # Arrange
    post_id = uuid.uuid4()

    # Create user schema
    user_id = uuid.uuid4()
    user_schema = UserSchema(
        id=user_id,
        email="test@example.com",
        display_name="Test User",
        is_verified=True,
        last_login=None,
        role="user",
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
    )

    # Create mock topic
    mock_topic = mock.AsyncMock()
    mock_topic.id = uuid.uuid4()

    # Create mock parent post
    mock_parent_post = mock.AsyncMock()
    mock_parent_post.id = post_id
    mock_parent_post.content = "Parent post content"
    mock_parent_post.author = user_schema
    mock_parent_post.topic = mock_topic
    mock_parent_post.parent_post = None

    # Create mock reply posts
    mock_reply1 = mock.AsyncMock()
    mock_reply1.id = uuid.uuid4()
    mock_reply1.content = "Reply post content 1"
    mock_reply1.author = user_schema
    mock_reply1.topic = mock_topic
    mock_reply1.topic.id = mock_topic.id  # Ensure topic.id is accessible
    mock_reply1.parent_post = mock_parent_post
    mock_reply1.parent_post.id = post_id  # Ensure parent_post.id is accessible
    mock_reply1.created_at = datetime.fromisoformat("2025-05-25T00:00:00")
    mock_reply1.updated_at = datetime.fromisoformat("2025-05-25T00:00:00")

    mock_reply2 = mock.AsyncMock()
    mock_reply2.id = uuid.uuid4()
    mock_reply2.content = "Reply post content 2"
    mock_reply2.author = user_schema
    mock_reply2.topic = mock_topic
    mock_reply2.topic.id = mock_topic.id  # Ensure topic.id is accessible
    mock_reply2.parent_post = mock_parent_post
    mock_reply2.parent_post.id = post_id  # Ensure parent_post.id is accessible
    mock_reply2.created_at = datetime.fromisoformat("2025-05-25T00:00:00")
    mock_reply2.updated_at = datetime.fromisoformat("2025-05-25T00:00:00")

    mock_replies = [mock_reply1, mock_reply2]
    mock_count = 2

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.list_post_replies.PostRepository.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_parent_post),
        ),
        mock.patch(
            "backend.routes.posts.list_post_replies.PostRepository.list_post_replies",
            new=mock.AsyncMock(return_value=(mock_replies, mock_count)),
        ),
        mock.patch(
            "backend.routes.posts.list_post_replies.PostRepository.get_reply_count",
            new=mock.AsyncMock(return_value=0),
        ),
    ):
        # Act
        result = await list_post_replies(post_id, skip=0, limit=20)

        # Assert
        assert isinstance(result, PostList)
        assert len(result.posts) == 2
        assert result.count == 2
        assert result.posts[0].parent_post_id == post_id
        assert result.posts[1].parent_post_id == post_id


@pytest.mark.asyncio
async def test_list_post_replies_parent_not_found():
    """Test listing replies when parent post does not exist."""
    # Arrange
    post_id = uuid.uuid4()

    # Mock dependencies - simulate parent post not found
    with mock.patch(
        "backend.routes.posts.list_post_replies.PostRepository.get_post_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await list_post_replies(post_id, skip=0, limit=20)

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Parent post not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_list_post_replies_pagination():
    """Test listing post replies with pagination."""
    # Arrange
    post_id = uuid.uuid4()

    # Create user schema
    user_id = uuid.uuid4()
    user_schema = UserSchema(
        id=user_id,
        email="test@example.com",
        display_name="Test User",
        is_verified=True,
        last_login=None,
        role="user",
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
    )

    # Create mock topic
    mock_topic = mock.AsyncMock()
    mock_topic.id = uuid.uuid4()

    # Create mock parent post
    mock_parent_post = mock.AsyncMock()
    mock_parent_post.id = post_id
    mock_parent_post.content = "Parent post content"
    mock_parent_post.author = user_schema
    mock_parent_post.topic = mock_topic
    mock_parent_post.parent_post = None

    # Create mock reply post
    mock_reply = mock.AsyncMock()
    mock_reply.id = uuid.uuid4()
    mock_reply.content = "Reply post content"
    mock_reply.author = user_schema
    mock_reply.topic = mock_topic
    mock_reply.topic.id = mock_topic.id  # Ensure topic.id is accessible
    mock_reply.parent_post = mock_parent_post
    mock_reply.parent_post.id = post_id  # Ensure parent_post.id is accessible
    mock_reply.created_at = datetime.fromisoformat("2025-05-25T00:00:00")
    mock_reply.updated_at = datetime.fromisoformat("2025-05-25T00:00:00")

    mock_replies = [mock_reply]
    mock_count = 30  # Total count is higher than the returned replies

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.list_post_replies.PostRepository.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_parent_post),
        ),
        mock.patch(
            "backend.routes.posts.list_post_replies.PostRepository.list_post_replies",
            new=mock.AsyncMock(return_value=(mock_replies, mock_count)),
        ),
        mock.patch(
            "backend.routes.posts.list_post_replies.PostRepository.get_reply_count",
            new=mock.AsyncMock(return_value=0),
        ),
    ):
        # Act
        # Skip first 10, get next 10
        result = await list_post_replies(post_id, skip=10, limit=10)

        # Assert
        assert isinstance(result, PostList)
        assert len(result.posts) == 1  # Only one reply in this page
        assert result.count == 30  # But total count is 30
