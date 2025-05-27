# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.posts.list_post_replies import list_post_replies
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse
from backend.schemas.user import UserSchema


@pytest.mark.asyncio
async def test_list_post_replies_success():
    """Test successful listing of post replies."""
    # Arrange
    post_id = uuid.uuid4()
    topic_id = uuid.uuid4()

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

    # Create mock parent post response
    mock_parent_post = PostResponse(
        id=post_id,
        content="Parent post content",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=None,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=2,
    )

    # Create mock reply post responses
    reply_id1 = uuid.uuid4()
    reply_id2 = uuid.uuid4()

    mock_reply1 = PostResponse(
        id=reply_id1,
        content="Reply post content 1",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=post_id,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=0,
    )

    mock_reply2 = PostResponse(
        id=reply_id2,
        content="Reply post content 2",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=post_id,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=0,
    )

    # Create mock PostList response
    mock_post_list = PostList(posts=[mock_reply1, mock_reply2], count=2)

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.list_post_replies.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_parent_post),
        ),
        mock.patch(
            "backend.routes.posts.list_post_replies.db_list_post_replies",
            new=mock.AsyncMock(return_value=mock_post_list),
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
        "backend.routes.posts.list_post_replies.get_post_by_id",
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
    topic_id = uuid.uuid4()

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

    # Create mock parent post response
    mock_parent_post = PostResponse(
        id=post_id,
        content="Parent post content",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=None,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=30,
    )

    # Create mock reply post response
    reply_id = uuid.uuid4()

    mock_reply = PostResponse(
        id=reply_id,
        content="Reply post content",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=post_id,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=0,
    )

    # Create mock PostList response with pagination
    mock_post_list = PostList(
        posts=[mock_reply],
        count=30,  # Total count is higher than the returned replies
    )

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.list_post_replies.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_parent_post),
        ),
        mock.patch(
            "backend.routes.posts.list_post_replies.db_list_post_replies",
            new=mock.AsyncMock(return_value=mock_post_list),
        ),
    ):
        # Act
        # Skip first 10, get next 10
        result = await list_post_replies(post_id, skip=10, limit=10)

        # Assert
        assert isinstance(result, PostList)
        assert len(result.posts) == 1  # Only one reply in this page
        assert result.count == 30  # But total count is 30
