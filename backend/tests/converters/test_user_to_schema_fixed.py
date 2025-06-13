from datetime import datetime
from unittest import mock
import uuid

import pytest

from backend.converters.user_to_schema import user_to_schema
from backend.db.models.user import User
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_user() -> mock.MagicMock:
    user_id = uuid.uuid4()

    # Create mock user
    user = mock.MagicMock(spec=User)
    user.id = user_id
    user.email = "user@example.com"
    user.display_name = "Test User"
    user.is_verified = True
    user.role = "user"
    user.is_locked = False
    user.created_at = datetime.now()
    user.updated_at = datetime.now()
    user.last_login = datetime.now()

    return user


@pytest.mark.asyncio
async def test_user_to_schema_basic(mock_user) -> None:
    """Test basic conversion of a user to a schema."""
    # Arrange
    # Mock Post.filter().count() to return 5
    post_filter_mock = mock.AsyncMock(return_value=5)
    post_filter = mock.MagicMock()
    post_filter.count = post_filter_mock

    # Mock RejectedPost.filter().count() to return 2
    rejected_post_filter_mock = mock.AsyncMock(return_value=2)
    rejected_post_filter = mock.MagicMock()
    rejected_post_filter.count = rejected_post_filter_mock

    with (
        mock.patch("backend.converters.user_to_schema.Post") as mock_post,
        # Mock the import inside the function
        mock.patch(
            "backend.db.models.rejected_post.RejectedPost", create=True
        ) as mock_rejected_post,
    ):
        # Setup mocks
        mock_post.filter.return_value = post_filter
        mock_rejected_post.filter.return_value = rejected_post_filter

        # Act
        schema = await user_to_schema(mock_user)

        # Assert
        assert isinstance(schema, UserSchema)
        assert schema.id == mock_user.id
        assert schema.email == mock_user.email
        assert schema.display_name == mock_user.display_name
        assert schema.is_verified == mock_user.is_verified
        assert schema.role == mock_user.role
        assert schema.is_locked == mock_user.is_locked
        assert schema.created_at == mock_user.created_at
        assert schema.updated_at == mock_user.updated_at
        assert schema.last_login == mock_user.last_login
        assert schema.approved_count == 5
        assert schema.rejected_count == 2

        # Verify function calls
        mock_post.filter.assert_called_once_with(author_id=mock_user.id)
        mock_rejected_post.filter.assert_called_once_with(author_id=mock_user.id)
        post_filter_mock.assert_awaited_once()
        rejected_post_filter_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_to_schema_with_no_posts(mock_user) -> None:
    """Test conversion of a user with no posts."""
    # Arrange
    # Mock Post.filter().count() to return 0
    post_filter_mock = mock.AsyncMock(return_value=0)
    post_filter = mock.MagicMock()
    post_filter.count = post_filter_mock

    # Mock RejectedPost.filter().count() to return 0
    rejected_post_filter_mock = mock.AsyncMock(return_value=0)
    rejected_post_filter = mock.MagicMock()
    rejected_post_filter.count = rejected_post_filter_mock

    with (
        mock.patch("backend.converters.user_to_schema.Post") as mock_post,
        # Mock the import inside the function
        mock.patch(
            "backend.db.models.rejected_post.RejectedPost", create=True
        ) as mock_rejected_post,
    ):
        # Setup mocks
        mock_post.filter.return_value = post_filter
        mock_rejected_post.filter.return_value = rejected_post_filter

        # Act
        schema = await user_to_schema(mock_user)

        # Assert
        assert schema.approved_count == 0
        assert schema.rejected_count == 0


@pytest.mark.asyncio
async def test_user_to_schema_with_different_roles(mock_user) -> None:
    """Test conversion with different user roles."""
    # Arrange
    roles = ["user", "moderator", "admin"]

    # Mock Post and RejectedPost
    with (
        mock.patch("backend.converters.user_to_schema.Post") as mock_post,
        # Mock the import inside the function
        mock.patch(
            "backend.db.models.rejected_post.RejectedPost", create=True
        ) as mock_rejected_post,
    ):
        # Setup post count mocks
        post_filter = mock.MagicMock()
        post_filter.count = mock.AsyncMock(return_value=1)
        mock_post.filter.return_value = post_filter

        rejected_post_filter = mock.MagicMock()
        rejected_post_filter.count = mock.AsyncMock(return_value=0)
        mock_rejected_post.filter.return_value = rejected_post_filter

        for role in roles:
            # Set the role
            mock_user.role = role

            # Act
            schema = await user_to_schema(mock_user)

            # Assert
            assert schema.role == role


@pytest.mark.asyncio
async def test_user_to_schema_with_locked_user(mock_user) -> None:
    """Test conversion with a locked user."""
    # Arrange
    mock_user.is_locked = True

    # Mock Post and RejectedPost
    with (
        mock.patch("backend.converters.user_to_schema.Post") as mock_post,
        # Mock the import inside the function
        mock.patch(
            "backend.db.models.rejected_post.RejectedPost", create=True
        ) as mock_rejected_post,
    ):
        # Setup post count mocks
        post_filter = mock.MagicMock()
        post_filter.count = mock.AsyncMock(return_value=1)
        mock_post.filter.return_value = post_filter

        rejected_post_filter = mock.MagicMock()
        rejected_post_filter.count = mock.AsyncMock(return_value=0)
        mock_rejected_post.filter.return_value = rejected_post_filter

        # Act
        schema = await user_to_schema(mock_user)

        # Assert
        assert schema.is_locked is True
