# Standard library imports
from unittest import mock
import uuid

from fastapi import HTTPException
from fastapi import status

# Third-party imports
import pytest
from tortoise.exceptions import ValidationError

# Project-specific imports
from backend.db.models.user import User
from backend.routes.api.posts.create_pending_post import create_pending_post
from backend.schemas.pending_post import PendingPostCreate
from backend.schemas.pending_post import PendingPostResponse
from backend.schemas.post import PostResponse
from backend.schemas.topic import TopicResponse


@pytest.fixture
def mock_user() -> mock.MagicMock:
    """Create a mock user for testing."""
    user = mock.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.username = "testuser"
    user.is_locked = False
    return user


@pytest.fixture
def mock_topic_response() -> mock.MagicMock:
    """Create a mock topic response for testing."""
    topic = mock.MagicMock(spec=TopicResponse)
    topic.id = uuid.uuid4()
    topic.title = "Test Topic"
    return topic


@pytest.fixture
def mock_post_response() -> mock.MagicMock:
    """Create a mock post response for testing."""
    post = mock.MagicMock(spec=PostResponse)
    post.id = uuid.uuid4()
    post.content = "Test Post Content"
    post.author_id = uuid.uuid4()
    post.topic_id = uuid.uuid4()
    post.parent_post_id = None
    return post


@pytest.fixture
def mock_pending_post_response() -> mock.MagicMock:
    """Create a mock pending post response for testing."""
    pending_post = mock.MagicMock(spec=PendingPostResponse)
    pending_post.id = uuid.uuid4()
    pending_post.content = "Test Pending Post Content"
    pending_post.author_id = uuid.uuid4()
    pending_post.topic_id = uuid.uuid4()
    pending_post.parent_post_id = None
    return pending_post


@pytest.mark.asyncio
async def test_create_pending_post_success(
    mock_user, mock_topic_response, mock_pending_post_response
):
    """Test successful creation of a pending post."""
    # Arrange
    topic_id = mock_topic_response.id
    post_data = PendingPostCreate(
        content="Test content",
        topic_id=topic_id,
        parent_post_id=None,
    )

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.api.posts.create_pending_post.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic_response),
        ) as mock_get_topic,
        mock.patch(
            "backend.routes.api.posts.create_pending_post.db_create_pending_post",
            new=mock.AsyncMock(return_value=mock_pending_post_response),
        ) as mock_create_pending_post,
        mock.patch(
            "backend.routes.api.posts.create_pending_post.schedule_post_moderation",
            new=mock.AsyncMock(),
        ) as mock_schedule_moderation,
    ):
        # Act
        result = await create_pending_post(post_data, mock_user)

        # Assert
        assert result == mock_pending_post_response

        # Verify function calls
        mock_get_topic.assert_awaited_once_with(topic_id)
        mock_create_pending_post.assert_awaited_once_with(
            user_id=mock_user.id,
            pending_post_data=post_data,
        )
        mock_schedule_moderation.assert_awaited_once_with(
            pending_post_id=mock_pending_post_response.id
        )


@pytest.mark.asyncio
async def test_create_pending_post_with_parent(
    mock_user, mock_topic_response, mock_post_response, mock_pending_post_response
):
    """Test creating a pending post with a parent post."""
    # Arrange
    topic_id = mock_topic_response.id
    parent_post_id = mock_post_response.id
    # Set the post's topic_id to match the requested topic
    mock_post_response.topic_id = topic_id

    post_data = PendingPostCreate(
        content="Test reply content",
        topic_id=topic_id,
        parent_post_id=parent_post_id,
    )

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.api.posts.create_pending_post.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic_response),
        ) as mock_get_topic,
        mock.patch(
            "backend.routes.api.posts.create_pending_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_post_response),
        ) as mock_get_post,
        mock.patch(
            "backend.routes.api.posts.create_pending_post.db_create_pending_post",
            new=mock.AsyncMock(return_value=mock_pending_post_response),
        ) as mock_create_pending_post,
        mock.patch(
            "backend.routes.api.posts.create_pending_post.schedule_post_moderation",
            new=mock.AsyncMock(),
        ) as mock_schedule_moderation,
    ):
        # Act
        result = await create_pending_post(post_data, mock_user)

        # Assert
        assert result == mock_pending_post_response

        # Verify function calls
        mock_get_topic.assert_awaited_once_with(topic_id)
        mock_get_post.assert_awaited_once_with(parent_post_id)
        mock_create_pending_post.assert_awaited_once_with(
            user_id=mock_user.id,
            pending_post_data=post_data,
        )
        mock_schedule_moderation.assert_awaited_once_with(
            pending_post_id=mock_pending_post_response.id
        )


@pytest.mark.asyncio
async def test_create_pending_post_topic_not_found(mock_user):
    """Test creating a pending post with a non-existent topic."""
    # Arrange
    topic_id = uuid.uuid4()
    post_data = PendingPostCreate(
        content="Test content",
        topic_id=topic_id,
        parent_post_id=None,
    )

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.api.posts.create_pending_post.get_topic_by_id",
            new=mock.AsyncMock(return_value=None),
        ) as mock_get_topic,
        pytest.raises(HTTPException) as exc_info,
    ):
        # Act
        await create_pending_post(post_data, mock_user)

    # Assert
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Topic not found"
    mock_get_topic.assert_awaited_once_with(topic_id)


@pytest.mark.asyncio
async def test_create_pending_post_parent_not_found(mock_user, mock_topic_response):
    """Test creating a pending post with a non-existent parent post."""
    # Arrange
    topic_id = mock_topic_response.id
    parent_post_id = uuid.uuid4()
    post_data = PendingPostCreate(
        content="Test reply content",
        topic_id=topic_id,
        parent_post_id=parent_post_id,
    )

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.api.posts.create_pending_post.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic_response),
        ) as mock_get_topic,
        mock.patch(
            "backend.routes.api.posts.create_pending_post.get_post_by_id",
            new=mock.AsyncMock(return_value=None),
        ) as mock_get_post,
        pytest.raises(HTTPException) as exc_info,
    ):
        # Act
        await create_pending_post(post_data, mock_user)

    # Assert
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Parent post not found"
    mock_get_topic.assert_awaited_once_with(topic_id)
    mock_get_post.assert_awaited_once_with(parent_post_id)


@pytest.mark.asyncio
async def test_create_pending_post_parent_topic_mismatch(
    mock_user, mock_topic_response, mock_post_response
):
    """Test creating a pending post with a parent post from a different topic."""
    # Arrange
    topic_id = mock_topic_response.id
    parent_post_id = mock_post_response.id
    # Set the post's topic_id to be different from the requested topic
    mock_post_response.topic_id = uuid.uuid4()

    post_data = PendingPostCreate(
        content="Test reply content",
        topic_id=topic_id,
        parent_post_id=parent_post_id,
    )

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.api.posts.create_pending_post.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic_response),
        ) as mock_get_topic,
        mock.patch(
            "backend.routes.api.posts.create_pending_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_post_response),
        ) as mock_get_post,
        pytest.raises(HTTPException) as exc_info,
    ):
        # Act
        await create_pending_post(post_data, mock_user)

    # Assert
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Parent post must belong to the same topic"
    mock_get_topic.assert_awaited_once_with(topic_id)
    mock_get_post.assert_awaited_once_with(parent_post_id)


@pytest.mark.asyncio
async def test_create_pending_post_validation_error(mock_user, mock_topic_response):
    """Test handling validation errors during pending post creation."""
    # Arrange
    topic_id = mock_topic_response.id
    post_data = PendingPostCreate(
        content="Test content",
        topic_id=topic_id,
        parent_post_id=None,
    )
    validation_error = ValidationError("Validation failed")

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.api.posts.create_pending_post.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic_response),
        ),
        mock.patch(
            "backend.routes.api.posts.create_pending_post.db_create_pending_post",
            new=mock.AsyncMock(side_effect=validation_error),
        ) as mock_create_pending_post,
        pytest.raises(HTTPException) as exc_info,
    ):
        # Act
        await create_pending_post(post_data, mock_user)

    # Assert
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == str(validation_error)
    mock_create_pending_post.assert_awaited_once_with(
        user_id=mock_user.id,
        pending_post_data=post_data,
    )
