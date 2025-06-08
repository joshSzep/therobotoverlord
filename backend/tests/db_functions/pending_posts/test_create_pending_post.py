# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.pending_post import PendingPost
from backend.db_functions.pending_posts.create_pending_post import create_pending_post
from backend.schemas.pending_post import PendingPostCreate
from backend.schemas.pending_post import PendingPostResponse


@pytest.fixture
def mock_pending_post() -> mock.MagicMock:
    pending_post = mock.MagicMock(spec=PendingPost)
    pending_post.id = uuid.uuid4()
    pending_post.content = "Test Pending Post Content"
    pending_post.author_id = uuid.uuid4()
    pending_post.topic_id = uuid.uuid4()
    pending_post.parent_post_id = None
    pending_post.created_at = mock.MagicMock()
    pending_post.updated_at = mock.MagicMock()
    return pending_post


@pytest.fixture
def mock_pending_post_response(mock_pending_post) -> PendingPostResponse:
    return mock.MagicMock(spec=PendingPostResponse)


@pytest.fixture
def mock_pending_post_create() -> PendingPostCreate:
    return PendingPostCreate(
        content="Test Pending Post Content",
        topic_id=uuid.uuid4(),
        parent_post_id=None,
    )


@pytest.mark.asyncio
async def test_create_pending_post_success(
    mock_pending_post, mock_pending_post_response, mock_pending_post_create
) -> None:
    # Arrange
    user_id = uuid.uuid4()

    # Mock the database query - RULE #10 compliance: only operates on PendingPost model
    with (
        mock.patch.object(
            PendingPost, "create", new=mock.AsyncMock(return_value=mock_pending_post)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.pending_posts.create_pending_post.pending_post_to_schema",
            new=mock.AsyncMock(return_value=mock_pending_post_response),
        ) as mock_converter,
    ):
        # Act
        result = await create_pending_post(
            user_id=user_id,
            pending_post_data=mock_pending_post_create,
        )

        # Assert
        assert result is not None
        assert result == mock_pending_post_response

        # Verify function calls
        mock_create.assert_called_once_with(
            author_id=user_id,
            topic_id=mock_pending_post_create.topic_id,
            content=mock_pending_post_create.content,
            parent_post_id=mock_pending_post_create.parent_post_id,
        )
        mock_converter.assert_called_once_with(mock_pending_post)


@pytest.mark.asyncio
async def test_create_pending_post_with_parent_post(
    mock_pending_post, mock_pending_post_response
) -> None:
    # Arrange
    user_id = uuid.uuid4()
    parent_post_id = uuid.uuid4()

    # Create pending post data with parent_post_id
    pending_post_data = PendingPostCreate(
        content="Test Pending Reply Content",
        topic_id=uuid.uuid4(),
        parent_post_id=parent_post_id,
    )

    # Mock the database query
    with (
        mock.patch.object(
            PendingPost, "create", new=mock.AsyncMock(return_value=mock_pending_post)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.pending_posts.create_pending_post.pending_post_to_schema",
            new=mock.AsyncMock(return_value=mock_pending_post_response),
        ) as mock_converter,
    ):
        # Act
        result = await create_pending_post(
            user_id=user_id,
            pending_post_data=pending_post_data,
        )

        # Assert
        assert result is not None
        assert result == mock_pending_post_response

        # Verify function calls
        mock_create.assert_called_once_with(
            author_id=user_id,
            topic_id=pending_post_data.topic_id,
            content=pending_post_data.content,
            parent_post_id=pending_post_data.parent_post_id,
        )
        mock_converter.assert_called_once_with(mock_pending_post)


@pytest.mark.asyncio
async def test_create_pending_post_database_error() -> None:
    # Arrange
    user_id = uuid.uuid4()
    pending_post_data = PendingPostCreate(
        content="Test Pending Post Content",
        topic_id=uuid.uuid4(),
    )
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        PendingPost, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_pending_post(
                user_id=user_id,
                pending_post_data=pending_post_data,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once_with(
            author_id=user_id,
            topic_id=pending_post_data.topic_id,
            content=pending_post_data.content,
            parent_post_id=pending_post_data.parent_post_id,
        )


@pytest.mark.asyncio
async def test_create_pending_post_invalid_data() -> None:
    # Arrange
    user_id = uuid.uuid4()

    # Create a mock PendingPostCreate with a valid structure
    pending_post_data = mock.MagicMock(spec=PendingPostCreate)
    pending_post_data.content = "Test Pending Post Content"
    pending_post_data.topic_id = "not-a-valid-uuid"  # This will cause a type error
    pending_post_data.parent_post_id = None

    # Mock the database query to raise a ValueError when trying to use the invalid UUID
    # Act & Assert
    with (
        mock.patch.object(
            PendingPost,
            "create",
            new=mock.AsyncMock(side_effect=ValueError("Invalid UUID format")),
        ),
        pytest.raises(ValueError),
    ):
        await create_pending_post(
            user_id=user_id,
            pending_post_data=pending_post_data,
        )
