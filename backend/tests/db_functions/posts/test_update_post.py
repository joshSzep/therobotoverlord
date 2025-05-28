# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.post import Post
from backend.db_functions.posts.update_post import update_post
from backend.schemas.post import PostResponse


@pytest.fixture
def mock_post() -> mock.MagicMock:
    post = mock.MagicMock(spec=Post)
    post.id = uuid.uuid4()
    post.content = "Original Content"
    post.author_id = uuid.uuid4()
    post.topic_id = uuid.uuid4()
    post.parent_post_id = None
    post.created_at = mock.MagicMock()
    post.updated_at = mock.MagicMock()
    return post


@pytest.fixture
def mock_post_response(mock_post) -> PostResponse:
    return mock.MagicMock(spec=PostResponse)


@pytest.mark.asyncio
async def test_update_post_success(mock_post, mock_post_response) -> None:
    # Arrange
    test_id = mock_post.id
    new_content = "Updated Content"

    # Mock the database query - RULE #10 compliance: only operates on Post model
    with (
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_get,
        mock.patch.object(mock_post, "save", new=mock.AsyncMock()) as mock_save,
        mock.patch(
            "backend.db_functions.posts.update_post.post_to_schema",
            new=mock.AsyncMock(return_value=mock_post_response),
        ) as mock_converter,
    ):
        # Act
        result = await update_post(post_id=test_id, content=new_content)

        # Assert
        assert result is not None
        assert result == mock_post_response
        assert mock_post.content == new_content

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_save.assert_called_once()
        mock_converter.assert_called_once_with(mock_post)


@pytest.mark.asyncio
async def test_update_post_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()
    new_content = "Updated Content"

    # Mock the database query
    with mock.patch.object(
        Post, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await update_post(post_id=test_id, content=new_content)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_update_post_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    new_content = "Updated Content"
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Post, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await update_post(post_id=test_id, content=new_content)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_update_post_save_error(mock_post) -> None:
    # Arrange
    test_id = mock_post.id
    new_content = "Updated Content"
    save_error = IntegrityError("Error saving post")

    # Mock the database query and save operation to raise an exception
    with (
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_get,
        mock.patch.object(
            mock_post, "save", new=mock.AsyncMock(side_effect=save_error)
        ) as mock_save,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await update_post(post_id=test_id, content=new_content)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_get.assert_called_once_with(id=test_id)
        mock_save.assert_called_once()
