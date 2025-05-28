# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.post import Post
from backend.db.models.user import User
from backend.db_functions.posts.is_user_post_author import is_user_post_author


@pytest.fixture
def mock_post() -> mock.MagicMock:
    post = mock.MagicMock(spec=Post)
    post.id = uuid.uuid4()
    post.content = "Test Post Content"
    post.author = mock.MagicMock(spec=User)
    post.author.id = uuid.uuid4()
    return post


@pytest.mark.asyncio
async def test_is_user_post_author_true(mock_post) -> None:
    # Arrange
    test_post_id = mock_post.id
    test_user_id = mock_post.author.id

    # Mock the database query - RULE #10 compliance: only operates on Post model
    with (
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_get,
        mock.patch.object(
            mock_post, "fetch_related", new=mock.AsyncMock()
        ) as mock_fetch,
    ):
        # Act
        result = await is_user_post_author(post_id=test_post_id, user_id=test_user_id)

        # Assert
        assert result is True

        # Verify function calls
        mock_get.assert_called_once_with(id=test_post_id)
        mock_fetch.assert_called_once_with("author")


@pytest.mark.asyncio
async def test_is_user_post_author_false(mock_post) -> None:
    # Arrange
    test_post_id = mock_post.id
    test_user_id = uuid.uuid4()  # Different user ID

    # Mock the database query
    with (
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_get,
        mock.patch.object(
            mock_post, "fetch_related", new=mock.AsyncMock()
        ) as mock_fetch,
    ):
        # Act
        result = await is_user_post_author(post_id=test_post_id, user_id=test_user_id)

        # Assert
        assert result is False

        # Verify function calls
        mock_get.assert_called_once_with(id=test_post_id)
        mock_fetch.assert_called_once_with("author")


@pytest.mark.asyncio
async def test_is_user_post_author_post_not_found() -> None:
    # Arrange
    test_post_id = uuid.uuid4()
    test_user_id = uuid.uuid4()

    # Mock the database query
    with mock.patch.object(
        Post, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await is_user_post_author(post_id=test_post_id, user_id=test_user_id)

        # Assert
        assert result is False
        mock_get.assert_called_once_with(id=test_post_id)


@pytest.mark.asyncio
async def test_is_user_post_author_database_error() -> None:
    # Arrange
    test_post_id = uuid.uuid4()
    test_user_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Post, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await is_user_post_author(post_id=test_post_id, user_id=test_user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_post_id)


@pytest.mark.asyncio
async def test_is_user_post_author_fetch_related_error(mock_post) -> None:
    # Arrange
    test_post_id = mock_post.id
    test_user_id = mock_post.author.id
    fetch_error = IntegrityError("Error fetching related models")

    # Mock the database query and fetch_related to raise an exception
    with (
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_get,
        mock.patch.object(
            mock_post, "fetch_related", new=mock.AsyncMock(side_effect=fetch_error)
        ) as mock_fetch,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await is_user_post_author(post_id=test_post_id, user_id=test_user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == fetch_error
        mock_get.assert_called_once_with(id=test_post_id)
        mock_fetch.assert_called_once_with("author")
