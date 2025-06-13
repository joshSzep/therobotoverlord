# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
import pytest

# Project-specific imports
from backend.converters.pending_post_to_schema import pending_post_to_schema
from backend.db.models.pending_post import PendingPost
from backend.schemas.pending_post import PendingPostResponse
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_pending_post() -> mock.MagicMock:
    """Create a mock pending post for testing."""
    # Create the main mock
    pending_post = mock.MagicMock(spec=PendingPost)
    pending_post.id = uuid.uuid4()
    pending_post.content = "Test Pending Post Content"
    pending_post.parent_post_id = None
    pending_post.created_at = datetime.now()
    pending_post.updated_at = datetime.now()

    # Create author mock
    author = mock.MagicMock()
    author.id = uuid.uuid4()
    author.username = "testuser"

    # Create topic mock
    topic = mock.MagicMock()
    topic.id = uuid.uuid4()
    topic.title = "Test Topic"

    # Set up author and topic as properties that will be accessed after fetch_related
    # In Tortoise ORM, these are accessed as properties after fetch_related is called
    pending_post.author = author
    pending_post.topic = topic

    # Mock fetch_related method to simulate loading related objects
    pending_post.fetch_related = mock.AsyncMock(return_value=pending_post)

    return pending_post


@pytest.fixture
def mock_user_schema() -> UserSchema:
    """Create a mock user schema for testing."""
    # Create a proper UserSchema with all required fields
    return UserSchema(
        id=uuid.uuid4(),
        email="testuser@example.com",
        display_name="Test User",
        is_verified=True,
        role="user",
        is_locked=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        approved_count=0,
        rejected_count=0,
    )


@pytest.mark.asyncio
async def test_pending_post_to_schema_basic(mock_pending_post, mock_user_schema):
    """Test basic conversion of a pending post to a schema."""
    # Arrange
    # Mock user_to_schema dependency
    with mock.patch(
        "backend.converters.pending_post_to_schema.user_to_schema",
        new=mock.AsyncMock(return_value=mock_user_schema),
    ) as mock_user_to_schema:
        # Act
        result = await pending_post_to_schema(mock_pending_post)

        # Assert
        assert isinstance(result, PendingPostResponse)
        assert result.id == mock_pending_post.id
        assert result.content == mock_pending_post.content
        assert result.author == mock_user_schema
        assert result.topic_id == mock_pending_post.topic.id
        assert result.parent_post_id == mock_pending_post.parent_post_id
        assert result.created_at == mock_pending_post.created_at
        assert result.updated_at == mock_pending_post.updated_at

        # Verify function calls
        mock_pending_post.fetch_related.assert_awaited_once_with("author", "topic")
        mock_user_to_schema.assert_awaited_once_with(mock_pending_post.author)


@pytest.mark.asyncio
async def test_pending_post_to_schema_with_parent(mock_pending_post, mock_user_schema):
    """Test conversion of a pending post with a parent post to a schema."""
    # Arrange
    parent_post_id = uuid.uuid4()
    mock_pending_post.parent_post_id = parent_post_id

    # Mock user_to_schema dependency
    with mock.patch(
        "backend.converters.pending_post_to_schema.user_to_schema",
        new=mock.AsyncMock(return_value=mock_user_schema),
    ):
        # Act
        result = await pending_post_to_schema(mock_pending_post)

        # Assert
        assert isinstance(result, PendingPostResponse)
        assert result.parent_post_id == parent_post_id


@pytest.mark.asyncio
async def test_pending_post_to_schema_author_fetch_error():
    """Test handling when author fetch fails."""
    # Arrange
    pending_post = mock.MagicMock(spec=PendingPost)
    pending_post.id = uuid.uuid4()
    pending_post.content = "Test Content"
    pending_post.parent_post_id = None

    # Mock fetch_related to fail
    fetch_error = Exception("Failed to fetch author")
    pending_post.fetch_related = mock.AsyncMock(side_effect=fetch_error)

    # Act and Assert
    with pytest.raises(Exception) as exc_info:
        await pending_post_to_schema(pending_post)

    # Verify the error is propagated
    assert exc_info.value == fetch_error
    pending_post.fetch_related.assert_awaited_once_with("author", "topic")


@pytest.mark.asyncio
async def test_pending_post_to_schema_topic_fetch_error():
    """Test handling when topic fetch fails."""
    # Arrange
    pending_post = mock.MagicMock(spec=PendingPost)
    pending_post.id = uuid.uuid4()
    pending_post.content = "Test Content"
    pending_post.parent_post_id = None

    # Mock fetch_related to succeed but user_to_schema to fail
    pending_post.fetch_related = mock.AsyncMock(return_value=pending_post)

    # Set up author property
    author = mock.MagicMock()
    pending_post.author = author

    # Set up topic property to be None
    # This will cause a validation error when the converter tries to access topic.id
    pending_post.topic = None

    # Act and Assert
    with pytest.raises(Exception) as exc_info:
        await pending_post_to_schema(pending_post)

    # Verify the error is propagated
    # The actual error is a ValidationError from Pydantic when trying to access topic.id
    # when topic is None
    assert "validation error" in str(exc_info.value).lower()
    pending_post.fetch_related.assert_awaited_once_with("author", "topic")


@pytest.mark.asyncio
async def test_pending_post_to_schema_user_to_schema_error(mock_pending_post):
    """Test handling when user_to_schema conversion fails."""
    # Arrange
    user_schema_error = Exception("Failed to convert user to schema")

    # Mock user_to_schema dependency to fail
    with mock.patch(
        "backend.converters.pending_post_to_schema.user_to_schema",
        new=mock.AsyncMock(side_effect=user_schema_error),
    ) as mock_user_to_schema:
        # Act and Assert
        with pytest.raises(Exception) as exc_info:
            await pending_post_to_schema(mock_pending_post)

        # Verify the error is propagated
        assert exc_info.value == user_schema_error
        mock_pending_post.fetch_related.assert_awaited_once_with("author", "topic")
        mock_user_to_schema.assert_awaited_once_with(mock_pending_post.author)
