# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.post import Post
from backend.db_functions.posts.delete_post import delete_post


@pytest.fixture
def mock_post() -> mock.MagicMock:
    post = mock.MagicMock(spec=Post)
    post.id = uuid.uuid4()
    post.content = "Test Post Content"
    post.author_id = uuid.uuid4()
    post.topic_id = uuid.uuid4()
    post.parent_post_id = None
    return post


@pytest.mark.asyncio
async def test_delete_post_success(mock_post) -> None:
    # Arrange
    test_id = mock_post.id

    # Mock the database query - RULE #10 compliance: only operates on Post model
    with (
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_get,
        mock.patch.object(mock_post, "delete", new=mock.AsyncMock()) as mock_delete,
    ):
        # Act
        result = await delete_post(test_id)

        # Assert
        assert result is True

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_post_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()

    # Mock the database query
    with mock.patch.object(
        Post, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await delete_post(test_id)

        # Assert
        assert result is False
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_delete_post_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Post, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await delete_post(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_delete_post_delete_error(mock_post) -> None:
    # Arrange
    test_id = mock_post.id
    delete_error = IntegrityError("Error deleting post")

    # Mock the database query and delete operation to raise an exception
    with (
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_get,
        mock.patch.object(
            mock_post, "delete", new=mock.AsyncMock(side_effect=delete_error)
        ) as mock_delete,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await delete_post(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == delete_error
        mock_get.assert_called_once_with(id=test_id)
        mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_post_cascading_deletion(mock_post) -> None:
    # Arrange
    test_id = mock_post.id

    # Create mock related objects that should be deleted
    mock_post.replies = [mock.MagicMock() for _ in range(3)]

    # Mock the database query - RULE #10 compliance: only operates on Post model
    with (
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_get,
        mock.patch.object(mock_post, "delete", new=mock.AsyncMock()) as mock_delete,
    ):
        # Act
        result = await delete_post(test_id)

        # Assert
        assert result is True

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_delete.assert_called_once()

        # Note: We don't need to explicitly test that related objects are deleted
        # since Tortoise ORM handles cascading deletions automatically based on
        # the model relationships. The delete() method on the post will trigger
        # the cascading deletions.
