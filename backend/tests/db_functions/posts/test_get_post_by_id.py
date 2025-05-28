# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.post import Post
from backend.db_functions.posts.get_post_by_id import get_post_by_id
from backend.schemas.post import PostResponse


@pytest.fixture
def mock_post() -> mock.MagicMock:
    post = mock.MagicMock(spec=Post)
    post.id = uuid.uuid4()
    post.content = "Test Post Content"
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
async def test_get_post_by_id_success(mock_post, mock_post_response) -> None:
    # Arrange
    test_id = mock_post.id

    # Mock the database query - RULE #10 compliance: only operates on Post model
    with (
        mock.patch.object(
            Post, "get_or_none", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.posts.get_post_by_id.post_to_schema",
            new=mock.AsyncMock(return_value=mock_post_response),
        ) as mock_converter,
    ):
        # Act
        result = await get_post_by_id(test_id)

        # Assert
        assert result is not None
        assert result == mock_post_response

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_converter.assert_called_once_with(mock_post)


@pytest.mark.asyncio
async def test_get_post_by_id_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()

    # Mock the database query
    with mock.patch.object(
        Post, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await get_post_by_id(test_id)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_get_post_by_id_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Post, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await get_post_by_id(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_get_post_by_id_invalid_uuid() -> None:
    # Arrange - We'll try to convert a string to UUID which should raise ValueError

    # Act & Assert
    with pytest.raises(ValueError):
        # We can't pass a string directly due to type checking, so we'll use uuid.UUID
        # with an invalid format to trigger the ValueError
        await get_post_by_id(uuid.UUID("not-a-valid-uuid"))
