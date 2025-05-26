from datetime import datetime
from unittest import mock
import uuid

from fastapi import HTTPException
import pytest

from backend.routes.auth.schemas import UserSchema
from backend.routes.posts.get_post import get_post
from backend.routes.posts.schemas import PostResponse


@pytest.mark.asyncio
async def test_get_post_success():
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

    # Create mock post
    mock_post = mock.AsyncMock()
    mock_post.id = post_id
    mock_post.content = "Test post content"
    mock_post.author = user_schema
    mock_post.topic = mock_topic
    mock_post.topic.id = mock_topic.id  # Ensure topic.id is accessible
    mock_post.parent_post = None
    mock_post.created_at = datetime.fromisoformat("2025-05-25T00:00:00")
    mock_post.updated_at = datetime.fromisoformat("2025-05-25T00:00:00")

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.get_post.PostRepository.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_post),
        ),
        mock.patch(
            "backend.routes.posts.get_post.PostRepository.get_reply_count",
            new=mock.AsyncMock(return_value=0),
        ),
    ):
        # Act
        result = await get_post(post_id)

        # Assert
        assert isinstance(result, PostResponse)
        assert result.id == post_id
        assert result.content == "Test post content"
        assert result.topic_id == mock_topic.id
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
