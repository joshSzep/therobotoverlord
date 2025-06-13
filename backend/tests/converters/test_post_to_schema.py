from datetime import datetime
from unittest import mock
import uuid

import pytest

from backend.converters.post_to_schema import post_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostResponse


@pytest.fixture
def mock_post() -> mock.MagicMock:
    post_id = uuid.uuid4()
    author_id = uuid.uuid4()
    topic_id = uuid.uuid4()

    # Create mock author
    mock_author = mock.MagicMock()
    mock_author.id = author_id
    mock_author.email = "user@example.com"
    mock_author.display_name = "Test User"
    mock_author.is_verified = True
    mock_author.role = "user"
    mock_author.is_locked = False
    mock_author.created_at = datetime.now()
    mock_author.updated_at = datetime.now()
    mock_author.last_login = datetime.now()

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Create mock post
    post = mock.MagicMock(spec=Post)
    post.id = post_id
    post.content = "Test post content"
    post.author = mock_author
    post.topic = mock_topic
    post.parent_post = None
    post.created_at = datetime.now()
    post.updated_at = datetime.now()

    # Set up mock methods
    post.fetch_related = mock.AsyncMock()

    # Mock Post.filter().count()
    mock_filter = mock.MagicMock()
    mock_count = mock.AsyncMock(return_value=5)
    mock_filter.count = mock_count

    # Patch Post.filter
    Post.filter = mock.MagicMock(return_value=mock_filter)

    return post


@pytest.mark.asyncio
async def test_post_to_schema(mock_post) -> None:
    # Convert the mock post to a schema
    schema = await post_to_schema(mock_post)

    # Verify fetch_related was called with correct parameters
    assert mock_post.fetch_related.call_count == 2
    mock_post.fetch_related.assert_any_call("author", "topic")
    mock_post.fetch_related.assert_any_call("parent_post")

    # Verify Post.filter was called with correct parameters for reply count
    Post.filter.assert_any_call(parent_post_id=mock_post.id)  # type: ignore[reportFunctionMemberAccess]

    # Verify the schema has the correct values
    assert isinstance(schema, PostResponse)
    assert schema.id == mock_post.id
    assert schema.content == mock_post.content
    assert schema.topic_id == mock_post.topic.id
    assert schema.parent_post_id is None
    assert schema.created_at == mock_post.created_at
    assert schema.updated_at == mock_post.updated_at
    assert schema.reply_count == 5


@pytest.fixture
def mock_post_with_parent() -> mock.MagicMock:
    post_id = uuid.uuid4()
    parent_id = uuid.uuid4()
    author_id = uuid.uuid4()
    topic_id = uuid.uuid4()

    # Create mock author
    mock_author = mock.MagicMock()
    mock_author.id = author_id
    mock_author.email = "user@example.com"
    mock_author.display_name = "Test User"
    mock_author.is_verified = True
    mock_author.role = "user"
    mock_author.is_locked = False
    mock_author.created_at = datetime.now()
    mock_author.updated_at = datetime.now()
    mock_author.last_login = datetime.now()

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Create mock parent post
    mock_parent = mock.MagicMock()
    mock_parent.id = parent_id

    # Create mock post
    post = mock.MagicMock(spec=Post)
    post.id = post_id
    post.content = "Test reply content"
    post.author = mock_author
    post.topic = mock_topic
    post.parent_post = mock_parent
    post.created_at = datetime.now()
    post.updated_at = datetime.now()

    # Set up mock methods
    post.fetch_related = mock.AsyncMock()

    # Mock Post.filter().count()
    mock_filter = mock.MagicMock()
    mock_count = mock.AsyncMock(return_value=0)
    mock_filter.count = mock_count

    # Patch Post.filter
    Post.filter = mock.MagicMock(return_value=mock_filter)

    return post


@pytest.mark.asyncio
async def test_post_to_schema_with_parent(mock_post_with_parent) -> None:
    # Convert the mock post to a schema
    schema = await post_to_schema(mock_post_with_parent)

    # Verify fetch_related was called with correct parameters
    assert mock_post_with_parent.fetch_related.call_count == 2
    mock_post_with_parent.fetch_related.assert_any_call("author", "topic")
    mock_post_with_parent.fetch_related.assert_any_call("parent_post")

    # Verify Post.filter was called with correct parameters for reply count
    Post.filter.assert_any_call(parent_post_id=mock_post_with_parent.id)  # type: ignore[reportFunctionMemberAccess]

    # Verify the schema has the correct values
    assert isinstance(schema, PostResponse)
    assert schema.id == mock_post_with_parent.id
    assert schema.content == mock_post_with_parent.content
    assert schema.topic_id == mock_post_with_parent.topic.id
    assert schema.parent_post_id == mock_post_with_parent.parent_post.id
    assert schema.created_at == mock_post_with_parent.created_at
    assert schema.updated_at == mock_post_with_parent.updated_at
    assert schema.reply_count == 0


@pytest.mark.asyncio
async def test_post_to_schema_missing_topic() -> None:
    """Test error handling when post has no associated topic."""
    # Create mock post without a topic
    post = mock.MagicMock(spec=Post)
    post.id = uuid.uuid4()
    post.content = "Test content"
    post.author = mock.MagicMock()
    post.topic = None  # Missing topic
    post.parent_post = None
    post.created_at = datetime.now()
    post.updated_at = datetime.now()

    # Set up mock methods
    post.fetch_related = mock.AsyncMock()

    # Mock Post.filter().count()
    mock_filter = mock.MagicMock()
    mock_filter.count = mock.AsyncMock(return_value=0)
    with mock.patch("backend.db.models.post.Post.filter", return_value=mock_filter):
        # Act and Assert
        with pytest.raises(ValueError, match=f"Post {post.id} has no associated topic"):
            await post_to_schema(post)

        # Verify fetch_related was called
        post.fetch_related.assert_any_call("author", "topic")


@pytest.mark.asyncio
async def test_post_to_schema_fetch_related_error() -> None:
    """Test error handling when fetch_related fails."""
    # Create mock post
    post = mock.MagicMock(spec=Post)
    post.id = uuid.uuid4()

    # Set up mock methods to fail
    fetch_error = Exception("Failed to fetch related data")
    post.fetch_related = mock.AsyncMock(side_effect=fetch_error)

    # Act and Assert
    with pytest.raises(Exception) as exc_info:
        await post_to_schema(post)

    # Verify the error is propagated
    assert exc_info.value == fetch_error
    post.fetch_related.assert_called_once()


@pytest.mark.asyncio
async def test_post_to_schema_user_to_schema_error() -> None:
    """Test error handling when user_to_schema conversion fails."""
    # Create mock post
    post_id = uuid.uuid4()

    # Create mock author
    mock_author = mock.MagicMock()

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = uuid.uuid4()

    # Create mock post
    post = mock.MagicMock(spec=Post)
    post.id = post_id
    post.content = "Test content"
    post.author = mock_author
    post.topic = mock_topic
    post.parent_post = None
    post.created_at = datetime.now()
    post.updated_at = datetime.now()

    # Set up mock methods
    post.fetch_related = mock.AsyncMock()

    # Mock Post.filter().count()
    mock_filter = mock.MagicMock()
    mock_filter.count = mock.AsyncMock(return_value=0)

    # Mock user_to_schema to fail
    user_schema_error = Exception("Failed to convert user to schema")

    with (
        mock.patch("backend.db.models.post.Post.filter", return_value=mock_filter),
        mock.patch(
            "backend.converters.post_to_schema.user_to_schema",
            side_effect=user_schema_error,
        ),
    ):
        # Act and Assert
        with pytest.raises(Exception) as exc_info:
            await post_to_schema(post)

        # Verify the error is propagated
        assert exc_info.value == user_schema_error


@pytest.mark.asyncio
async def test_post_to_schema_many_replies() -> None:
    """Test post with many replies."""
    # Create mock post
    post_id = uuid.uuid4()

    # Create mock author
    mock_author = mock.MagicMock()
    mock_author.id = uuid.uuid4()

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = uuid.uuid4()

    # Create mock post
    post = mock.MagicMock(spec=Post)
    post.id = post_id
    post.content = "Test post with many replies"
    post.author = mock_author
    post.topic = mock_topic
    post.parent_post = None
    post.created_at = datetime.now()
    post.updated_at = datetime.now()

    # Set up mock methods
    post.fetch_related = mock.AsyncMock()

    # Mock Post.filter().count() to return a large number
    mock_filter = mock.MagicMock()
    mock_filter.count = mock.AsyncMock(return_value=1000)  # Many replies

    # Create a proper mock UserSchema that matches the expected structure
    from backend.schemas.user import UserSchema

    mock_user_schema = UserSchema(
        id=mock_author.id,
        email="test_user@example.com",  # EmailStr will validate this
        display_name="Test User",
        is_verified=True,
        role="user",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        approved_count=0,
        rejected_count=0,
    )

    with (
        mock.patch("backend.db.models.post.Post.filter", return_value=mock_filter),
        mock.patch(
            "backend.converters.post_to_schema.user_to_schema",
            mock.AsyncMock(return_value=mock_user_schema),
        ),
    ):
        # Act
        schema = await post_to_schema(post)

        # Assert
        assert schema.reply_count == 1000
