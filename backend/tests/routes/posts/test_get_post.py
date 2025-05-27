from datetime import datetime
from unittest import mock
import uuid

from fastapi import HTTPException
import pytest

from backend.routes.posts.get_post import get_post
from backend.schemas.post import PostResponse
from backend.schemas.user import UserSchema


@pytest.mark.asyncio
async def test_get_post_success():
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

    # Create mock post response directly as a schema
    mock_post_response = PostResponse(
        id=post_id,
        content="Test post content",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=None,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=0,
    )

    # Mock dependencies
    with mock.patch(
        "backend.routes.posts.get_post.PostRepository.get_post_by_id",
        new=mock.AsyncMock(return_value=mock_post_response),
    ):
        # Act
        result = await get_post(post_id)

        # Assert
        assert isinstance(result, PostResponse)
        assert result.id == post_id
        assert result.content == "Test post content"
        assert result.topic_id == topic_id
        assert result.parent_post_id is None
        assert result.reply_count == 0


@pytest.mark.asyncio
async def test_get_post_not_found():
    # Arrange
    post_id = uuid.uuid4()

    # Mock dependencies - simulate post not found
    with mock.patch(
        "backend.routes.posts.get_post.PostRepository.get_post_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_post(post_id)

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Post not found" in excinfo.value.detail
