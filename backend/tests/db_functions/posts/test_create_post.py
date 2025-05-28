# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.post import Post
from backend.db_functions.posts.create_post import create_post
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
async def test_create_post_success(mock_post, mock_post_response) -> None:
    # Arrange
    content = "Test Post Content"
    author_id = uuid.uuid4()
    topic_id = uuid.uuid4()

    # Mock the database query - RULE #10 compliance: only operates on Post model
    with (
        mock.patch.object(
            Post, "create", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.posts.create_post.post_to_schema",
            new=mock.AsyncMock(return_value=mock_post_response),
        ) as mock_converter,
    ):
        # Act
        result = await create_post(
            content=content,
            author_id=author_id,
            topic_id=topic_id,
        )

        # Assert
        assert result is not None
        assert result == mock_post_response

        # Verify function calls
        mock_create.assert_called_once_with(
            using_db=None,
            content=content,
            author_id=author_id,
            topic_id=topic_id,
        )
        mock_converter.assert_called_once_with(mock_post)


@pytest.mark.asyncio
async def test_create_post_with_parent_post(mock_post, mock_post_response) -> None:
    # Arrange
    content = "Test Reply Content"
    author_id = uuid.uuid4()
    topic_id = uuid.uuid4()
    parent_post_id = uuid.uuid4()

    # Mock the database query
    with (
        mock.patch.object(
            Post, "create", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.posts.create_post.post_to_schema",
            new=mock.AsyncMock(return_value=mock_post_response),
        ) as mock_converter,
    ):
        # Act
        result = await create_post(
            content=content,
            author_id=author_id,
            topic_id=topic_id,
            parent_post_id=parent_post_id,
        )

        # Assert
        assert result is not None
        assert result == mock_post_response

        # Verify function calls
        mock_create.assert_called_once_with(
            using_db=None,
            content=content,
            author_id=author_id,
            topic_id=topic_id,
            parent_post_id=parent_post_id,
        )
        mock_converter.assert_called_once_with(mock_post)


@pytest.mark.asyncio
async def test_create_post_database_error() -> None:
    # Arrange
    content = "Test Post Content"
    author_id = uuid.uuid4()
    topic_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Post, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_post(
                content=content,
                author_id=author_id,
                topic_id=topic_id,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once_with(
            using_db=None,
            content=content,
            author_id=author_id,
            topic_id=topic_id,
        )


@pytest.mark.asyncio
async def test_create_post_invalid_data() -> None:
    # Arrange
    content = "Test Post Content"
    author_id = uuid.uuid4()

    # Act & Assert
    with pytest.raises(ValueError):
        # We can't pass a string directly due to type checking, so we'll use uuid.UUID
        # with an invalid format to trigger the ValueError
        await create_post(
            content=content,
            author_id=author_id,
            topic_id=uuid.UUID("not-a-valid-uuid"),  # This will raise a ValueError
        )
