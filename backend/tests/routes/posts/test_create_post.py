from datetime import datetime
from unittest import mock
import uuid

from fastapi import HTTPException
import pytest

from backend.routes.posts.create_post import create_post
from backend.schemas.post import PostCreate
from backend.schemas.post import PostResponse
from backend.schemas.user import UserSchema


@pytest.mark.asyncio
async def test_create_post_success():
    """Test successful post creation."""
    # Arrange
    post_data = PostCreate(
        content="Test post content",
        topic_id=uuid.uuid4(),
    )

    # Create mock topic response
    mock_topic = mock.AsyncMock()
    mock_topic.id = post_data.topic_id

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.is_verified = True
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = datetime(2025, 5, 25)
    mock_user.updated_at = datetime(2025, 5, 25)

    # Create mock post response
    post_id = uuid.uuid4()

    # Create a mock that will be returned by the repository
    mock_post_response = mock.AsyncMock()
    mock_post_response.id = post_id
    mock_post_response.content = post_data.content
    mock_post_response.author_id = mock_user.id
    mock_post_response.author = mock_user
    mock_post_response.topic_id = post_data.topic_id
    mock_post_response.parent_post_id = None
    mock_post_response.created_at = datetime(2025, 5, 25)
    mock_post_response.updated_at = datetime(2025, 5, 25)

    # Create a proper UserSchema for the author field
    user_schema = UserSchema(
        id=mock_user.id,
        email=mock_user.email,
        display_name=mock_user.display_name,
        is_verified=mock_user.is_verified,
        last_login=mock_user.last_login,
        role=mock_user.role,
        created_at=mock_user.created_at,
        updated_at=mock_user.updated_at,
    )

    # Create a PostResponse object that will be returned by the repository
    post_response = PostResponse(
        id=post_id,
        content=post_data.content,
        author=user_schema,
        topic_id=post_data.topic_id,
        parent_post_id=None,
        created_at=datetime(2025, 5, 25),
        updated_at=datetime(2025, 5, 25),
        reply_count=0,
    )

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.create_post.TopicRepository.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.posts.create_post.PostRepository.get_post_by_id",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.routes.posts.create_post.PostRepository.create_post",
            new=mock.AsyncMock(return_value=post_response),
        ),
    ):
        # Act
        result = await create_post(post_data, mock_user)

        # Assert
        assert isinstance(result, PostResponse)
        assert result.content == post_data.content
        assert result.topic_id == post_data.topic_id
        assert result.parent_post_id is None
        assert result.reply_count == 0


@pytest.mark.asyncio
async def test_create_post_topic_not_found():
    """Test post creation with non-existent topic."""
    # Arrange
    post_data = PostCreate(
        content="Test post content",
        topic_id=uuid.uuid4(),
    )

    # Create mock user
    mock_user = mock.AsyncMock()

    # Mock dependencies - simulate topic not found
    with mock.patch(
        "backend.routes.posts.create_post.TopicRepository.get_topic_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await create_post(post_data, mock_user)

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Topic not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_create_post_with_parent():
    """Test creating a post with a parent post (reply)."""
    # Arrange
    parent_post_id = uuid.uuid4()
    topic_id = uuid.uuid4()

    post_data = PostCreate(
        content="Test reply content",
        topic_id=topic_id,
        parent_post_id=parent_post_id,
    )

    # Create mock topic response
    mock_topic = mock.AsyncMock()
    mock_topic.id = topic_id

    # Create mock parent post response
    mock_parent_post = mock.AsyncMock()
    mock_parent_post.id = parent_post_id
    mock_parent_post.topic_id = topic_id

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.is_verified = True
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = datetime(2025, 5, 25)
    mock_user.updated_at = datetime(2025, 5, 25)

    # Create mock post response
    post_id = uuid.uuid4()

    # Create a mock that will be returned by the repository
    mock_post_response = mock.AsyncMock()
    mock_post_response.id = post_id
    mock_post_response.content = post_data.content
    mock_post_response.author_id = mock_user.id
    mock_post_response.author = mock_user
    mock_post_response.topic_id = topic_id
    mock_post_response.parent_post_id = parent_post_id
    mock_post_response.created_at = datetime(2025, 5, 25)
    mock_post_response.updated_at = datetime(2025, 5, 25)

    # Create a proper UserSchema for the author field
    user_schema = UserSchema(
        id=mock_user.id,
        email=mock_user.email,
        display_name=mock_user.display_name,
        is_verified=mock_user.is_verified,
        last_login=mock_user.last_login,
        role=mock_user.role,
        created_at=mock_user.created_at,
        updated_at=mock_user.updated_at,
    )

    # Create a PostResponse object that will be returned by the repository
    post_response = PostResponse(
        id=post_id,
        content=post_data.content,
        author=user_schema,
        topic_id=topic_id,
        parent_post_id=parent_post_id,
        created_at=datetime(2025, 5, 25),
        updated_at=datetime(2025, 5, 25),
        reply_count=0,
    )

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.create_post.TopicRepository.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.posts.create_post.PostRepository.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_parent_post),
        ),
        mock.patch(
            "backend.routes.posts.create_post.PostRepository.create_post",
            new=mock.AsyncMock(return_value=post_response),
        ),
    ):
        # Act
        result = await create_post(post_data, mock_user)

        # Assert
        assert isinstance(result, PostResponse)
        assert result.content == post_data.content
        assert result.topic_id == post_data.topic_id
        assert result.parent_post_id == parent_post_id


@pytest.mark.asyncio
async def test_create_post_parent_not_found():
    """Test post creation with non-existent parent post."""
    # Arrange
    post_data = PostCreate(
        content="Test post content",
        topic_id=uuid.uuid4(),
        parent_post_id=uuid.uuid4(),
    )

    # Create mock topic
    mock_topic = mock.AsyncMock()
    mock_topic.id = post_data.topic_id

    # Create mock user
    mock_user = mock.AsyncMock()

    # Mock dependencies - simulate parent post not found
    with (
        mock.patch(
            "backend.routes.posts.create_post.TopicRepository.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.posts.create_post.PostRepository.get_post_by_id",
            new=mock.AsyncMock(return_value=None),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await create_post(post_data, mock_user)

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Parent post not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_create_post_parent_different_topic():
    """Test post creation with parent post from different topic."""
    # Arrange
    post_data = PostCreate(
        content="Test post content",
        topic_id=uuid.uuid4(),
        parent_post_id=uuid.uuid4(),
    )

    # Create mock topic response
    mock_topic = mock.AsyncMock()
    mock_topic.id = post_data.topic_id

    # Create mock parent post response with different topic
    mock_parent_post = mock.AsyncMock()
    mock_parent_post.id = post_data.parent_post_id
    mock_parent_post.topic_id = uuid.uuid4()  # Different topic ID

    # Create mock user
    mock_user = mock.AsyncMock()

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.create_post.TopicRepository.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.posts.create_post.PostRepository.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_parent_post),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await create_post(post_data, mock_user)

        # Verify the exception details
        assert excinfo.value.status_code == 400
        assert "Parent post must belong to the same topic" in excinfo.value.detail
