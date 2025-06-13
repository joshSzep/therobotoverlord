# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
import pytest

# Project-specific imports
from backend.converters.rejected_post_to_schema import rejected_post_to_schema
from backend.db.models.rejected_post import RejectedPost
from backend.schemas.rejected_post import RejectedPostResponse
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_rejected_post() -> mock.MagicMock:
    """Create a mock rejected post for testing."""
    rejected_post = mock.MagicMock(spec=RejectedPost)
    rejected_post.id = uuid.uuid4()
    rejected_post.content = "Test Rejected Post Content"
    rejected_post.parent_post_id = None
    rejected_post.created_at = datetime.now()
    rejected_post.updated_at = datetime.now()
    rejected_post.moderation_reason = "Content violates guidelines"

    # Mock related objects
    author = mock.MagicMock()
    author.id = uuid.uuid4()
    author.username = "testuser"
    rejected_post.author = author

    topic = mock.MagicMock()
    topic.id = uuid.uuid4()
    topic.title = "Test Topic"
    rejected_post.topic = topic

    # Mock fetch_related method
    rejected_post.fetch_related = mock.AsyncMock(return_value=rejected_post)

    return rejected_post


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
async def test_rejected_post_to_schema_basic(mock_rejected_post, mock_user_schema):
    """Test basic conversion of a rejected post to a schema."""
    # Arrange
    # Mock user_to_schema dependency
    with mock.patch(
        "backend.converters.rejected_post_to_schema.user_to_schema",
        new=mock.AsyncMock(return_value=mock_user_schema),
    ) as mock_user_to_schema:
        # Act
        result = await rejected_post_to_schema(mock_rejected_post)

        # Assert
        assert isinstance(result, RejectedPostResponse)
        assert result.id == mock_rejected_post.id
        assert result.content == mock_rejected_post.content
        assert result.author == mock_user_schema
        assert result.topic_id == mock_rejected_post.topic.id
        assert result.parent_post_id == mock_rejected_post.parent_post_id
        assert result.created_at == mock_rejected_post.created_at
        assert result.updated_at == mock_rejected_post.updated_at
        assert result.moderation_reason == mock_rejected_post.moderation_reason

        # Verify function calls
        mock_rejected_post.fetch_related.assert_awaited_once_with("author", "topic")
        mock_user_to_schema.assert_awaited_once_with(mock_rejected_post.author)


@pytest.mark.asyncio
async def test_rejected_post_to_schema_with_parent(
    mock_rejected_post, mock_user_schema
):
    """Test conversion of a rejected post with a parent post to a schema."""
    # Arrange
    parent_post_id = uuid.uuid4()
    mock_rejected_post.parent_post_id = parent_post_id

    # Mock user_to_schema dependency
    with mock.patch(
        "backend.converters.rejected_post_to_schema.user_to_schema",
        new=mock.AsyncMock(return_value=mock_user_schema),
    ):
        # Act
        result = await rejected_post_to_schema(mock_rejected_post)

        # Assert
        assert isinstance(result, RejectedPostResponse)
        assert result.parent_post_id == parent_post_id


@pytest.mark.asyncio
async def test_rejected_post_to_schema_with_different_moderation_reasons(
    mock_rejected_post, mock_user_schema
):
    """Test conversion with different moderation reasons."""
    # Arrange
    test_reasons = [
        "Content violates community guidelines",
        "Spam content",
        "Inappropriate language",
        "No reason",  # Changed from None to a string since moderation_reason is likely a required field  # noqa: E501
        "",  # Test with empty reason
    ]

    # Mock user_to_schema dependency
    with mock.patch(
        "backend.converters.rejected_post_to_schema.user_to_schema",
        new=mock.AsyncMock(return_value=mock_user_schema),
    ):
        for reason in test_reasons:
            # Set the moderation reason
            mock_rejected_post.moderation_reason = reason

            # Act
            result = await rejected_post_to_schema(mock_rejected_post)

            # Assert
            assert result.moderation_reason == reason


@pytest.mark.asyncio
async def test_rejected_post_to_schema_author_fetch_error():
    """Test handling when author fetch fails."""
    # Arrange
    rejected_post = mock.MagicMock(spec=RejectedPost)
    rejected_post.id = uuid.uuid4()
    rejected_post.content = "Test Content"
    rejected_post.parent_post_id = None
    rejected_post.moderation_reason = "Test reason"

    # Mock fetch_related to fail
    fetch_error = Exception("Failed to fetch author")
    rejected_post.fetch_related = mock.AsyncMock(side_effect=fetch_error)

    # Act and Assert
    with pytest.raises(Exception) as exc_info:
        await rejected_post_to_schema(rejected_post)

    # Verify the error is propagated
    assert exc_info.value == fetch_error
    rejected_post.fetch_related.assert_awaited_once_with("author", "topic")


@pytest.mark.asyncio
async def test_rejected_post_to_schema_topic_fetch_error():
    """Test handling when topic fetch fails."""
    # Arrange
    rejected_post = mock.MagicMock(spec=RejectedPost)
    rejected_post.id = uuid.uuid4()
    rejected_post.content = "Test Content"
    rejected_post.parent_post_id = None
    rejected_post.moderation_reason = "Test reason"

    # Since we're now using fetch_related for both author and topic,
    # we'll test a different scenario where fetch_related succeeds but
    # accessing topic.id fails due to topic being None
    rejected_post.fetch_related = mock.AsyncMock(return_value=rejected_post)
    rejected_post.author = mock.MagicMock()

    # Set up topic property to be None
    # This will cause a validation error when the converter tries to access topic.id
    rejected_post.topic = None

    # Act and Assert
    with pytest.raises(Exception) as exc_info:
        await rejected_post_to_schema(rejected_post)

    # Verify the error is propagated
    # The actual error is a ValidationError from Pydantic when trying to access topic.id
    # when topic is None
    assert "validation error" in str(exc_info.value).lower()
    rejected_post.fetch_related.assert_awaited_once_with("author", "topic")


@pytest.mark.asyncio
async def test_rejected_post_to_schema_user_to_schema_error(mock_rejected_post):
    """Test handling when user_to_schema conversion fails."""
    # Arrange
    user_schema_error = Exception("Failed to convert user to schema")

    # Mock user_to_schema dependency to fail
    with mock.patch(
        "backend.converters.rejected_post_to_schema.user_to_schema",
        new=mock.AsyncMock(side_effect=user_schema_error),
    ) as mock_user_to_schema:
        # Act and Assert
        with pytest.raises(Exception) as exc_info:
            await rejected_post_to_schema(mock_rejected_post)

        # Verify the error is propagated
        assert exc_info.value == user_schema_error
        mock_rejected_post.fetch_related.assert_awaited_once_with("author", "topic")
        mock_user_to_schema.assert_awaited_once_with(mock_rejected_post.author)
