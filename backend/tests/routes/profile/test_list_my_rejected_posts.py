from unittest import mock
import uuid

import pytest

from backend.db.models.user import User
from backend.routes.profile.list_my_rejected_posts import list_my_rejected_posts
from backend.schemas.rejected_post import RejectedPostList
from backend.schemas.rejected_post import RejectedPostResponse
from backend.schemas.user import UserSchema
from backend.utils.datetime import now_utc


@pytest.fixture
def mock_user() -> mock.MagicMock:
    """Returns a mock User object."""
    user = mock.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.username = "test_user"
    return user


@pytest.fixture
def mock_rejected_posts() -> RejectedPostList:
    """Returns a mock RejectedPostList object."""
    user_id = uuid.uuid4()
    topic_id = uuid.uuid4()

    mock_author = UserSchema(
        id=user_id,
        email="test@example.com",
        display_name="Test User",
        is_verified=True,
        role="user",
        created_at=now_utc(),
        updated_at=now_utc(),
    )

    rejected_posts = [
        RejectedPostResponse(
            id=uuid.uuid4(),
            content="First rejected post",
            author=mock_author,
            topic_id=topic_id,
            moderation_reason="Content violates guidelines",
            created_at=now_utc(),
            updated_at=now_utc(),
        ),
        RejectedPostResponse(
            id=uuid.uuid4(),
            content="Second rejected post",
            author=mock_author,
            topic_id=topic_id,
            moderation_reason="Duplicate content",
            created_at=now_utc(),
            updated_at=now_utc(),
        ),
    ]

    return RejectedPostList(
        rejected_posts=rejected_posts,
        count=2,
    )


@pytest.mark.asyncio
async def test_list_my_rejected_posts_success(mock_user, mock_rejected_posts):
    """Test successful retrieval of user's rejected posts."""
    # Arrange
    limit = 10
    offset = 0

    # Mock dependencies
    with mock.patch(
        "backend.routes.profile.list_my_rejected_posts.list_rejected_posts",
        new=mock.AsyncMock(return_value=mock_rejected_posts),
    ) as mock_list_rejected:
        # Act
        result = await list_my_rejected_posts(
            current_user=mock_user,
            limit=limit,
            offset=offset,
        )

        # Assert
        assert result == mock_rejected_posts
        assert len(result.rejected_posts) == 2
        assert result.count == 2
        mock_list_rejected.assert_called_once_with(
            user_id=mock_user.id,
            limit=limit,
            offset=offset,
        )


@pytest.mark.asyncio
async def test_list_my_rejected_posts_empty(mock_user):
    """Test retrieval of empty rejected posts list."""
    # Arrange
    limit = 10
    offset = 0
    empty_list = RejectedPostList(
        rejected_posts=[],
        count=0,
    )

    # Mock dependencies
    with mock.patch(
        "backend.routes.profile.list_my_rejected_posts.list_rejected_posts",
        new=mock.AsyncMock(return_value=empty_list),
    ) as mock_list_rejected:
        # Act
        result = await list_my_rejected_posts(
            current_user=mock_user,
            limit=limit,
            offset=offset,
        )

        # Assert
        assert result == empty_list
        assert len(result.rejected_posts) == 0
        assert result.count == 0
        mock_list_rejected.assert_called_once_with(
            user_id=mock_user.id,
            limit=limit,
            offset=offset,
        )


@pytest.mark.asyncio
async def test_list_my_rejected_posts_pagination(mock_user, mock_rejected_posts):
    """Test pagination of rejected posts."""
    # Arrange
    limit = 5
    offset = 10
    paginated_list = RejectedPostList(
        rejected_posts=mock_rejected_posts.rejected_posts,
        count=20,  # Total of 20 posts, but only returning 2
    )

    # Mock dependencies
    with mock.patch(
        "backend.routes.profile.list_my_rejected_posts.list_rejected_posts",
        new=mock.AsyncMock(return_value=paginated_list),
    ) as mock_list_rejected:
        # Act
        result = await list_my_rejected_posts(
            current_user=mock_user,
            limit=limit,
            offset=offset,
        )

        # Assert
        assert result == paginated_list
        assert result.count == 20
        mock_list_rejected.assert_called_once_with(
            user_id=mock_user.id,
            limit=limit,
            offset=offset,
        )
