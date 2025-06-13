from unittest import mock
import uuid

from fastapi import HTTPException
import pytest

from backend.routes.pending_posts.moderate_pending_post import moderate_pending_post


@pytest.fixture
def mock_pending_post():
    """Mock pending post for testing."""
    pending_post = mock.MagicMock()
    pending_post.id = uuid.uuid4()
    pending_post.content = "Test pending post content"
    pending_post.author_id = uuid.uuid4()
    pending_post.topic_id = uuid.uuid4()
    return pending_post


@pytest.fixture
def mock_user():
    """Mock user for testing."""
    user = mock.MagicMock()
    user.id = uuid.uuid4()
    user.role = "moderator"
    user.is_verified = True
    return user


@pytest.mark.asyncio
async def test_moderate_pending_post_approve_success(mock_pending_post, mock_user):
    """Test successful approval of pending post."""
    # Arrange
    pending_post_id = mock_pending_post.id
    action = "approve"

    with (
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.get_pending_post_by_id"
        ) as mock_get_pending,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.approve_and_create_post"
        ) as mock_approve,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.check_is_admin"
        ) as mock_check_admin,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.get_current_user"
        ) as mock_get_user,
    ):
        mock_get_pending.return_value = mock_pending_post
        mock_approve.return_value = None
        mock_check_admin.return_value = True
        mock_get_user.return_value = mock_user

        # Act
        result = await moderate_pending_post(
            pending_post_id, action, "", current_user=mock_user
        )

        # Assert
        assert result == mock_pending_post
        mock_get_pending.assert_called_once_with(pending_post_id)
        mock_approve.assert_called_once_with(pending_post_id=pending_post_id)


@pytest.mark.asyncio
async def test_moderate_pending_post_reject_success(mock_pending_post, mock_user):
    """Test successful rejection of pending post."""
    # Arrange
    pending_post_id = mock_pending_post.id
    action = "reject"
    reason = "Test rejection reason"

    with (
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.get_pending_post_by_id"
        ) as mock_get_pending,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.reject_pending_post"
        ) as mock_reject,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.check_is_admin"
        ) as mock_check_admin,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.get_current_user"
        ) as mock_get_user,
    ):
        mock_get_pending.return_value = mock_pending_post
        mock_reject.return_value = None
        mock_check_admin.return_value = True
        mock_get_user.return_value = mock_user

        # Act
        result = await moderate_pending_post(
            pending_post_id, action, reason, current_user=mock_user
        )

        # Assert
        assert result == mock_pending_post
        mock_get_pending.assert_called_once_with(pending_post_id)
        mock_reject.assert_called_once_with(
            pending_post_id=pending_post_id, moderation_reason=reason
        )


@pytest.mark.asyncio
async def test_moderate_pending_post_unauthorized_user():
    """Test moderation with unauthorized user."""
    # Arrange
    pending_post_id = uuid.uuid4()
    action = "approve"
    mock_user = mock.MagicMock()
    mock_user.id = uuid.uuid4()
    mock_pending_post = mock.MagicMock()

    with (
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.get_pending_post_by_id"
        ) as mock_get_pending,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.check_is_admin"
        ) as mock_check_admin,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.get_current_user"
        ) as mock_get_user,
    ):
        mock_get_pending.return_value = mock_pending_post
        mock_check_admin.return_value = False
        mock_get_user.return_value = mock_user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await moderate_pending_post(
                pending_post_id, action, "", current_user=mock_user
            )

        assert exc_info.value.status_code == 403
        assert "Only administrators can moderate posts" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_moderate_pending_post_not_found():
    """Test moderation with non-existent pending post."""
    # Arrange
    pending_post_id = uuid.uuid4()
    action = "approve"
    mock_user = mock.MagicMock()
    mock_user.id = uuid.uuid4()

    with (
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.get_pending_post_by_id"
        ) as mock_get_pending,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.get_current_user"
        ) as mock_get_user,
    ):
        mock_get_pending.return_value = None
        mock_get_user.return_value = mock_user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await moderate_pending_post(
                pending_post_id, action, "", current_user=mock_user
            )

        assert exc_info.value.status_code == 404
        error_msg = f"Pending post with ID {pending_post_id} not found"
        assert error_msg in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_moderate_pending_post_invalid_action(mock_pending_post, mock_user):
    """Test moderation with invalid action."""
    # Arrange
    pending_post_id = mock_pending_post.id
    action = "invalid_action"

    with (
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.get_pending_post_by_id"
        ) as mock_get_pending,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.check_is_admin"
        ) as mock_check_admin,
        mock.patch(
            "backend.routes.pending_posts.moderate_pending_post.get_current_user"
        ) as mock_get_user,
    ):
        mock_get_pending.return_value = mock_pending_post
        mock_check_admin.return_value = True
        mock_get_user.return_value = mock_user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await moderate_pending_post(
                pending_post_id, action, "", current_user=mock_user
            )

        assert exc_info.value.status_code == 400
        error_msg = 'Action must be either "approve" or "reject"'
        assert error_msg in str(exc_info.value.detail)
