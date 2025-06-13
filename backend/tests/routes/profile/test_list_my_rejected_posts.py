from datetime import datetime
from unittest import mock
import uuid

from fastapi import HTTPException
import pytest

from backend.routes.profile.list_my_rejected_posts import list_my_rejected_posts
from backend.schemas.rejected_post import RejectedPostList
from backend.schemas.rejected_post import RejectedPostResponse
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_user():
    """Mock user for testing."""
    user = mock.MagicMock()
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.is_verified = True
    return user


@pytest.fixture
def mock_rejected_posts(mock_user):
    """Mock rejected posts for testing."""

    # Create proper UserSchema for the author
    user_schema = UserSchema(
        id=mock_user.id,
        email=mock_user.email,
        display_name="Test User",
        is_verified=mock_user.is_verified,
        role="user",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    posts = []
    for i in range(3):
        post = RejectedPostResponse(
            id=uuid.uuid4(),
            content=f"Rejected post content {i}",
            author=user_schema,
            topic_id=uuid.uuid4(),
            parent_post_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            moderation_reason=f"Rejection reason {i}",
            topic=None,
        )
        posts.append(post)
    return posts


@pytest.mark.asyncio
async def test_list_my_rejected_posts_success(mock_user, mock_rejected_posts):
    """Test successful retrieval of user's rejected posts."""
    # Arrange
    limit = 10
    offset = 0

    with (
        mock.patch(
            "backend.routes.profile.list_my_rejected_posts.get_current_user"
        ) as mock_get_user,
        mock.patch(
            "backend.routes.profile.list_my_rejected_posts.list_rejected_posts"
        ) as mock_list_rejected,
    ):
        mock_get_user.return_value = mock_user
        mock_list_rejected.return_value = RejectedPostList(
            rejected_posts=mock_rejected_posts, count=len(mock_rejected_posts)
        )

        # Act
        result = await list_my_rejected_posts(
            current_user=mock_user, limit=limit, offset=offset
        )

        # Assert
        assert result.rejected_posts == mock_rejected_posts
        assert result.count == len(mock_rejected_posts)
        mock_list_rejected.assert_called_once_with(
            user_id=mock_user.id, limit=limit, offset=offset
        )


@pytest.mark.asyncio
async def test_list_my_rejected_posts_empty_results(mock_user):
    """Test retrieval when user has no rejected posts."""
    # Arrange
    limit = 10
    offset = 0
    empty_posts = []

    with (
        mock.patch(
            "backend.routes.profile.list_my_rejected_posts.get_current_user"
        ) as mock_get_user,
        mock.patch(
            "backend.routes.profile.list_my_rejected_posts.list_rejected_posts"
        ) as mock_list_rejected,
    ):
        mock_get_user.return_value = mock_user
        mock_list_rejected.return_value = RejectedPostList(
            rejected_posts=empty_posts, count=0
        )

        # Act
        result = await list_my_rejected_posts(
            current_user=mock_user, limit=limit, offset=offset
        )

        # Assert
        assert result.rejected_posts == empty_posts
        assert result.count == 0
        mock_list_rejected.assert_called_once_with(
            user_id=mock_user.id, limit=limit, offset=offset
        )


@pytest.mark.asyncio
async def test_list_my_rejected_posts_pagination(mock_user, mock_rejected_posts):
    """Test pagination parameters are passed correctly."""
    # Arrange
    limit = 5
    offset = 5

    with (
        mock.patch(
            "backend.routes.profile.list_my_rejected_posts.get_current_user"
        ) as mock_get_user,
        mock.patch(
            "backend.routes.profile.list_my_rejected_posts.list_rejected_posts"
        ) as mock_list_rejected,
    ):
        mock_get_user.return_value = mock_user
        mock_list_rejected.return_value = RejectedPostList(
            rejected_posts=mock_rejected_posts[:2], count=2
        )  # Simulate page 2

        # Act
        result = await list_my_rejected_posts(
            current_user=mock_user, limit=limit, offset=offset
        )

        # Assert
        assert len(result.rejected_posts) == 2
        assert result.count == 2
        mock_list_rejected.assert_called_once_with(
            user_id=mock_user.id, limit=limit, offset=offset
        )


@pytest.mark.asyncio
async def test_list_my_rejected_posts_unauthenticated():
    """Test access without authentication."""
    # Arrange
    with mock.patch(
        "backend.routes.profile.list_my_rejected_posts.get_current_user"
    ) as mock_get_user:
        mock_get_user.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_my_rejected_posts(current_user=None)

        assert exc_info.value.status_code == 401
        assert "Authentication required" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_list_my_rejected_posts_database_error(mock_user):
    """Test handling of database errors."""
    # Arrange
    limit = 10
    offset = 0
    db_error = Exception("Database connection error")

    with (
        mock.patch(
            "backend.routes.profile.list_my_rejected_posts.get_current_user"
        ) as mock_get_user,
        mock.patch(
            "backend.routes.profile.list_my_rejected_posts.list_rejected_posts",
            side_effect=db_error,
        ),
    ):
        mock_get_user.return_value = mock_user

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await list_my_rejected_posts(
                current_user=mock_user, limit=limit, offset=offset
            )

        assert exc_info.value == db_error
