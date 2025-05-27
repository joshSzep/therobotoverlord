# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
import pytest

# Project-specific imports
from backend.routes.posts.list_posts import list_posts
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse
from backend.schemas.user import UserSchema


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

    topic_id = uuid.uuid4()

    # Create mock post responses as schemas
    post_id1 = uuid.uuid4()
    post_id2 = uuid.uuid4()

    mock_post1 = PostResponse(
        id=post_id1,
        content="Test post content 1",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=None,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=0,
    )

    mock_post2 = PostResponse(
        id=post_id2,
        content="Test post content 2",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=None,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=0,
    )

    # Create mock PostList response
    mock_post_list = PostList(posts=[mock_post1, mock_post2], count=2)

    # Mock dependencies
    with mock.patch(
        "backend.routes.posts.list_posts.db_list_posts",
        new=mock.AsyncMock(return_value=mock_post_list),
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

    # Create mock post response as schema
    post_id = uuid.uuid4()

    mock_post = PostResponse(
        id=post_id,
        content="Test post content",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=None,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=0,
    )

    # Create mock PostList response
    mock_post_list = PostList(posts=[mock_post], count=1)

    # Mock dependencies
    with mock.patch(
        "backend.routes.posts.list_posts.db_list_posts",
        new=mock.AsyncMock(return_value=mock_post_list),
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
    topic_id = uuid.uuid4()

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

    # Create mock post response as schema
    post_id = uuid.uuid4()

    mock_post = PostResponse(
        id=post_id,
        content="Test post content",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=None,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=0,
    )

    # Create mock PostList response
    mock_post_list = PostList(posts=[mock_post], count=1)

    # Mock dependencies
    with mock.patch(
        "backend.routes.posts.list_posts.db_list_posts",
        new=mock.AsyncMock(return_value=mock_post_list),
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

    topic_id = uuid.uuid4()

    # Create mock post response as schema
    post_id = uuid.uuid4()

    mock_post = PostResponse(
        id=post_id,
        content="Test post content",
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=None,
        created_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        updated_at=datetime.fromisoformat("2025-05-25T00:00:00"),
        reply_count=0,
    )

    # Create mock PostList response with pagination
    mock_post_list = PostList(
        posts=[mock_post],
        count=30,  # Total count is higher than the returned posts
    )

    # Mock dependencies
    with mock.patch(
        "backend.routes.posts.list_posts.db_list_posts",
        new=mock.AsyncMock(return_value=mock_post_list),
    ):
        # Act
        result = await list_posts(skip=10, limit=10)  # Skip first 10, get next 10

        # Assert
        assert isinstance(result, PostList)
        assert len(result.posts) == 1  # Only one post in this page
        assert result.count == 30  # But total count is 30
