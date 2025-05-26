from datetime import datetime
from unittest import mock
import uuid

import pytest

from backend.routes.auth.schemas import UserSchema
from backend.routes.posts.list_posts import list_posts
from backend.routes.posts.schemas import PostList


@pytest.mark.asyncio
async def test_list_posts_no_filters():
    """Test listing posts without any filters."""
    # Arrange
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

    # Create mock posts
    mock_post1 = mock.AsyncMock()
    mock_post1.id = uuid.uuid4()
    mock_post1.content = "Test post content 1"
    mock_post1.author = user_schema
    mock_post1.topic = mock_topic
    mock_post1.topic.id = mock_topic.id  # Ensure topic.id is accessible
    mock_post1.parent_post = None
    mock_post1.created_at = datetime.fromisoformat("2025-05-25T00:00:00")
    mock_post1.updated_at = datetime.fromisoformat("2025-05-25T00:00:00")

    mock_post2 = mock.AsyncMock()
    mock_post2.id = uuid.uuid4()
    mock_post2.content = "Test post content 2"
    mock_post2.author = user_schema
    mock_post2.topic = mock_topic
    mock_post2.topic.id = mock_topic.id  # Ensure topic.id is accessible
    mock_post2.parent_post = None
    mock_post2.created_at = datetime.fromisoformat("2025-05-25T00:00:00")
    mock_post2.updated_at = datetime.fromisoformat("2025-05-25T00:00:00")

    mock_posts = [mock_post1, mock_post2]
    mock_count = 2

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.list_posts.PostRepository.list_posts",
            new=mock.AsyncMock(return_value=(mock_posts, mock_count)),
        ),
        mock.patch(
            "backend.routes.posts.list_posts.PostRepository.get_reply_count",
            new=mock.AsyncMock(return_value=0),
        ),
    ):
        # Act
        result = await list_posts(skip=0, limit=20)

        # Assert
        assert isinstance(result, PostList)
        assert len(result.posts) == 2
        assert result.count == 2


@pytest.mark.asyncio
async def test_list_posts_with_topic_filter():
    """Test listing posts with topic filter."""
    # Arrange
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

    # Create mock topic
    mock_topic = mock.AsyncMock()
    mock_topic.id = topic_id

    # Create mock posts
    mock_post = mock.AsyncMock()
    mock_post.id = uuid.uuid4()
    mock_post.content = "Test post content"
    mock_post.author = user_schema
    mock_post.topic = mock_topic
    mock_post.topic.id = mock_topic.id  # Ensure topic.id is accessible
    mock_post.parent_post = None
    mock_post.created_at = datetime.fromisoformat("2025-05-25T00:00:00")
    mock_post.updated_at = datetime.fromisoformat("2025-05-25T00:00:00")

    mock_posts = [mock_post]
    mock_count = 1

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.list_posts.PostRepository.list_posts",
            new=mock.AsyncMock(return_value=(mock_posts, mock_count)),
        ),
        mock.patch(
            "backend.routes.posts.list_posts.PostRepository.get_reply_count",
            new=mock.AsyncMock(return_value=0),
        ),
    ):
        # Act
        result = await list_posts(skip=0, limit=20, topic_id=topic_id)

        # Assert
        assert isinstance(result, PostList)
        assert len(result.posts) == 1
        assert result.count == 1
        assert result.posts[0].topic_id == topic_id


@pytest.mark.asyncio
async def test_list_posts_with_author_filter():
    """Test listing posts with author filter."""
    # Arrange
    author_id = uuid.uuid4()

    # Create user schema
    user_schema = UserSchema(
        id=author_id,
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

    # Create mock posts
    mock_post = mock.AsyncMock()
    mock_post.id = uuid.uuid4()
    mock_post.content = "Test post content"
    mock_post.author = user_schema
    mock_post.topic = mock_topic
    mock_post.topic.id = mock_topic.id  # Ensure topic.id is accessible
    mock_post.parent_post = None
    mock_post.created_at = datetime.fromisoformat("2025-05-25T00:00:00")
    mock_post.updated_at = datetime.fromisoformat("2025-05-25T00:00:00")

    mock_posts = [mock_post]
    mock_count = 1

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.list_posts.PostRepository.list_posts",
            new=mock.AsyncMock(return_value=(mock_posts, mock_count)),
        ),
        mock.patch(
            "backend.routes.posts.list_posts.PostRepository.get_reply_count",
            new=mock.AsyncMock(return_value=0),
        ),
    ):
        # Act
        result = await list_posts(skip=0, limit=20, author_id=author_id)

        # Assert
        assert isinstance(result, PostList)
        assert len(result.posts) == 1
        assert result.count == 1
        assert result.posts[0].author.id == author_id


@pytest.mark.asyncio
async def test_list_posts_pagination():
    """Test listing posts with pagination."""
    # Arrange
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

    # Create mock posts
    mock_post = mock.AsyncMock()
    mock_post.id = uuid.uuid4()
    mock_post.content = "Test post content"
    mock_post.author = user_schema
    mock_post.topic = mock_topic
    mock_post.topic.id = mock_topic.id  # Ensure topic.id is accessible
    mock_post.parent_post = None
    mock_post.created_at = datetime.fromisoformat("2025-05-25T00:00:00")
    mock_post.updated_at = datetime.fromisoformat("2025-05-25T00:00:00")

    mock_posts = [mock_post]
    mock_count = 30  # Total count is higher than the returned posts

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.list_posts.PostRepository.list_posts",
            new=mock.AsyncMock(return_value=(mock_posts, mock_count)),
        ),
        mock.patch(
            "backend.routes.posts.list_posts.PostRepository.get_reply_count",
            new=mock.AsyncMock(return_value=0),
        ),
    ):
        # Act
        result = await list_posts(skip=10, limit=10)  # Skip first 10, get next 10

        # Assert
        assert isinstance(result, PostList)
        assert len(result.posts) == 1  # Only one post in this page
        assert result.count == 30  # But total count is 30
