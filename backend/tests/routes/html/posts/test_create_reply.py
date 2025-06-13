# Standard library imports
from unittest import mock
import uuid
from uuid import UUID

from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import RedirectResponse

# Third-party imports
import pytest

# Project-specific imports
from backend.routes.html.posts.create_reply import create_reply_handler
from backend.routes.html.schemas.user import UserResponse


@pytest.fixture
def mock_request() -> mock.MagicMock:
    """Create a mock request for testing."""
    return mock.MagicMock(spec=Request)


@pytest.fixture
def mock_user() -> mock.MagicMock:
    """Create a mock user for testing."""
    user = mock.MagicMock(spec=UserResponse)
    user.id = uuid.uuid4()
    user.username = "testuser"
    return user


@pytest.mark.asyncio
async def test_create_reply_handler_success(mock_request, mock_user):
    """Test successful reply creation."""
    # Arrange
    topic_id = str(uuid.uuid4())
    parent_post_id = str(uuid.uuid4())
    content = "Test reply content"

    # Mock dependencies
    with mock.patch(
        "backend.routes.html.posts.create_reply.create_post", new=mock.AsyncMock()
    ) as mock_create_post:
        # Act
        response = await create_reply_handler(
            request=mock_request,
            current_user=mock_user,
            topic_id=topic_id,
            parent_post_id=parent_post_id,
            content=content,
        )

        # Assert
        assert isinstance(response, RedirectResponse)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert f"/html/topics/{topic_id}/" in response.headers["location"]

        # Verify create_post was called with correct parameters
        mock_create_post.assert_awaited_once_with(
            author_id=mock_user.id,
            topic_id=UUID(topic_id),
            content=content,
            parent_post_id=UUID(parent_post_id),
        )


@pytest.mark.asyncio
async def test_create_reply_handler_unauthenticated(mock_request):
    """Test reply creation with unauthenticated user."""
    # Arrange
    topic_id = str(uuid.uuid4())
    parent_post_id = str(uuid.uuid4())
    content = "Test reply content"

    # Act
    response = await create_reply_handler(
        request=mock_request,
        current_user=None,  # No user is authenticated
        topic_id=topic_id,
        parent_post_id=parent_post_id,
        content=content,
    )

    # Assert
    assert isinstance(response, RedirectResponse)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert "/html/auth/login/" in response.headers["location"]


@pytest.mark.asyncio
async def test_create_reply_handler_invalid_topic_uuid(mock_request, mock_user):
    """Test reply creation with invalid topic UUID."""
    # Arrange
    topic_id = "not-a-uuid"
    parent_post_id = str(uuid.uuid4())
    content = "Test reply content"

    # Act and Assert
    with pytest.raises(HTTPException) as exc_info:
        await create_reply_handler(
            request=mock_request,
            current_user=mock_user,
            topic_id=topic_id,
            parent_post_id=parent_post_id,
            content=content,
        )

    # Verify exception details
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid topic_id or parent_post_id format" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_reply_handler_invalid_parent_uuid(mock_request, mock_user):
    """Test reply creation with invalid parent post UUID."""
    # Arrange
    topic_id = str(uuid.uuid4())
    parent_post_id = "not-a-uuid"
    content = "Test reply content"

    # Act and Assert
    with pytest.raises(HTTPException) as exc_info:
        await create_reply_handler(
            request=mock_request,
            current_user=mock_user,
            topic_id=topic_id,
            parent_post_id=parent_post_id,
            content=content,
        )

    # Verify exception details
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid topic_id or parent_post_id format" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_reply_handler_create_post_error(mock_request, mock_user):
    """Test handling errors from create_post function."""
    # Arrange
    topic_id = str(uuid.uuid4())
    parent_post_id = str(uuid.uuid4())
    content = "Test reply content"
    error_message = "Database error"

    # Mock dependencies with error
    with mock.patch(
        "backend.routes.html.posts.create_reply.create_post",
        new=mock.AsyncMock(side_effect=Exception(error_message)),
    ) as mock_create_post:
        # Act and Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_reply_handler(
                request=mock_request,
                current_user=mock_user,
                topic_id=topic_id,
                parent_post_id=parent_post_id,
                content=content,
            )

        # Verify exception details
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert error_message in exc_info.value.detail

        # Verify create_post was called
        mock_create_post.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_reply_handler_debug_logging(mock_request, mock_user):
    """Test that debug logging is performed."""
    # Arrange
    topic_id = str(uuid.uuid4())
    parent_post_id = str(uuid.uuid4())
    content = "Test reply content"

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.html.posts.create_reply.create_post", new=mock.AsyncMock()
        ),
        mock.patch("backend.routes.html.posts.create_reply.logging") as mock_logging,
    ):
        # Act
        await create_reply_handler(
            request=mock_request,
            current_user=mock_user,
            topic_id=topic_id,
            parent_post_id=parent_post_id,
            content=content,
        )

        # Assert
        # Verify debug logs were called
        assert mock_logging.debug.call_count >= 3
        # Check for specific log messages
        mock_logging.debug.assert_any_call(
            f"Reply form submission: topic_id={topic_id}"
        )
        mock_logging.debug.assert_any_call(f"parent_post_id={parent_post_id}")
        mock_logging.debug.assert_any_call(f"Content: {content}")
