from datetime import datetime
from unittest import mock
import uuid

import pytest

from backend.converters.topic_to_schema import topic_to_schema
from backend.db.models.topic import Topic
from backend.schemas.topic import TopicResponse


@pytest.fixture
def mock_topic() -> mock.MagicMock:
    topic_id = uuid.uuid4()
    author_id = uuid.uuid4()

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
    topic = mock.MagicMock(spec=Topic)
    topic.id = topic_id
    topic.title = "Test Topic"
    topic.description = "Test topic description"
    topic.author = mock_author
    topic.created_at = datetime.now()
    topic.updated_at = datetime.now()

    # Create empty topic_tags list
    topic.topic_tags = []

    # Set up mock methods
    topic.fetch_related = mock.AsyncMock()

    return topic


@pytest.mark.asyncio
async def test_topic_to_schema_without_tags(mock_topic) -> None:
    # Convert the mock topic to a schema
    schema = await topic_to_schema(mock_topic)

    # Verify fetch_related was called with correct parameters
    mock_topic.fetch_related.assert_awaited_once_with("author", "topic_tags__tag")

    # Verify the schema has the correct values
    assert isinstance(schema, TopicResponse)
    assert schema.id == mock_topic.id
    assert schema.title == mock_topic.title
    assert schema.description == mock_topic.description
    assert schema.created_at == mock_topic.created_at
    assert schema.updated_at == mock_topic.updated_at
    assert len(schema.tags) == 0


@pytest.fixture
def mock_topic_with_tags() -> mock.MagicMock:
    topic_id = uuid.uuid4()
    author_id = uuid.uuid4()
    tag1_id = uuid.uuid4()
    tag2_id = uuid.uuid4()

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

    # Create mock tags
    mock_tag1 = mock.MagicMock()
    mock_tag1.id = tag1_id
    mock_tag1.name = "Tag1"
    mock_tag1.slug = "tag1"
    mock_tag1.created_at = datetime.now()
    mock_tag1.updated_at = datetime.now()

    mock_tag2 = mock.MagicMock()
    mock_tag2.id = tag2_id
    mock_tag2.name = "Tag2"
    mock_tag2.slug = "tag2"
    mock_tag2.created_at = datetime.now()
    mock_tag2.updated_at = datetime.now()

    # Create mock topic_tags
    mock_topic_tag1 = mock.MagicMock()
    mock_topic_tag1.tag = mock_tag1

    mock_topic_tag2 = mock.MagicMock()
    mock_topic_tag2.tag = mock_tag2

    # Create mock topic
    topic = mock.MagicMock(spec=Topic)
    topic.id = topic_id
    topic.title = "Test Topic with Tags"
    topic.description = "Test topic description with tags"
    topic.author = mock_author
    topic.created_at = datetime.now()
    topic.updated_at = datetime.now()

    # Set topic_tags list
    topic.topic_tags = [mock_topic_tag1, mock_topic_tag2]

    # Set up mock methods
    topic.fetch_related = mock.AsyncMock()

    return topic


@pytest.mark.asyncio
async def test_topic_to_schema_with_tags(mock_topic_with_tags) -> None:
    # Convert the mock topic to a schema
    schema = await topic_to_schema(mock_topic_with_tags)

    # Verify fetch_related was called with correct parameters
    mock_topic_with_tags.fetch_related.assert_awaited_once_with(
        "author", "topic_tags__tag"
    )

    # Verify the schema has the correct values
    assert isinstance(schema, TopicResponse)
    assert schema.id == mock_topic_with_tags.id
    assert schema.title == mock_topic_with_tags.title
    assert schema.description == mock_topic_with_tags.description
    assert schema.created_at == mock_topic_with_tags.created_at
    assert schema.updated_at == mock_topic_with_tags.updated_at

    # Verify tags
    assert len(schema.tags) == 2
    assert schema.tags[0].name == "Tag1"
    assert schema.tags[1].name == "Tag2"


@pytest.mark.asyncio
async def test_topic_to_schema_missing_author() -> None:
    """Test error handling when topic has no associated author."""
    # Create mock topic without an author
    topic = mock.MagicMock(spec=Topic)
    topic.id = uuid.uuid4()
    topic.title = "Test Topic"
    topic.description = "Test topic description"
    topic.author = None  # Missing author
    topic.created_at = datetime.now()
    topic.updated_at = datetime.now()
    topic.topic_tags = []

    # Set up mock methods
    topic.fetch_related = mock.AsyncMock()

    # Mock Post.filter().count()
    mock_filter = mock.MagicMock()
    mock_filter.count = mock.AsyncMock(return_value=0)

    with mock.patch("backend.db.models.post.Post.filter", return_value=mock_filter):
        # Act and Assert
        with pytest.raises(AttributeError):
            await topic_to_schema(topic)

        # Verify fetch_related was called
        topic.fetch_related.assert_awaited_once_with("author", "topic_tags__tag")


@pytest.mark.asyncio
async def test_topic_to_schema_fetch_related_error() -> None:
    """Test error handling when fetch_related fails."""
    # Create mock topic
    topic = mock.MagicMock(spec=Topic)
    topic.id = uuid.uuid4()

    # Set up mock methods to fail
    fetch_error = Exception("Failed to fetch related data")
    topic.fetch_related = mock.AsyncMock(side_effect=fetch_error)

    # Act and Assert
    with pytest.raises(Exception) as exc_info:
        await topic_to_schema(topic)

    # Verify the error is propagated
    assert exc_info.value == fetch_error
    topic.fetch_related.assert_called_once()


@pytest.mark.asyncio
async def test_topic_to_schema_tag_to_schema_error() -> None:
    """Test error handling when tag_to_schema conversion fails."""
    # Create mock topic with tags
    topic_id = uuid.uuid4()

    # Create mock author
    mock_author = mock.MagicMock()

    # Create mock tag
    mock_tag = mock.MagicMock()

    # Create mock topic_tag
    mock_topic_tag = mock.MagicMock()
    mock_topic_tag.tag = mock_tag

    # Create mock topic
    topic = mock.MagicMock(spec=Topic)
    topic.id = topic_id
    topic.title = "Test Topic"
    topic.description = "Test topic description"
    topic.author = mock_author
    topic.created_at = datetime.now()
    topic.updated_at = datetime.now()
    topic.topic_tags = [mock_topic_tag]

    # Set up mock methods
    topic.fetch_related = mock.AsyncMock()

    # Mock Post.filter().count()
    mock_filter = mock.MagicMock()
    mock_filter.count = mock.AsyncMock(return_value=0)

    # Mock tag_to_schema to fail
    tag_schema_error = Exception("Failed to convert tag to schema")

    with (
        mock.patch("backend.db.models.post.Post.filter", return_value=mock_filter),
        mock.patch(
            "backend.converters.topic_to_schema.tag_to_schema",
            side_effect=tag_schema_error,
        ),
    ):
        # Act and Assert
        with pytest.raises(Exception) as exc_info:
            await topic_to_schema(topic)

        # Verify the error is propagated
        assert exc_info.value == tag_schema_error


@pytest.mark.asyncio
async def test_topic_to_schema_user_to_schema_error() -> None:
    """Test error handling when user_to_schema conversion fails."""
    # Create mock topic
    topic_id = uuid.uuid4()

    # Create mock author
    mock_author = mock.MagicMock()

    # Create mock topic
    topic = mock.MagicMock(spec=Topic)
    topic.id = topic_id
    topic.title = "Test Topic"
    topic.description = "Test topic description"
    topic.author = mock_author
    topic.created_at = datetime.now()
    topic.updated_at = datetime.now()
    topic.topic_tags = []

    # Set up mock methods
    topic.fetch_related = mock.AsyncMock()

    # Mock Post.filter().count()
    mock_filter = mock.MagicMock()
    mock_filter.count = mock.AsyncMock(return_value=0)

    # Mock user_to_schema to fail
    user_schema_error = Exception("Failed to convert user to schema")

    with (
        mock.patch("backend.db.models.post.Post.filter", return_value=mock_filter),
        mock.patch(
            "backend.converters.topic_to_schema.user_to_schema",
            side_effect=user_schema_error,
        ),
    ):
        # Act and Assert
        with pytest.raises(Exception) as exc_info:
            await topic_to_schema(topic)

        # Verify the error is propagated
        assert exc_info.value == user_schema_error


@pytest.mark.asyncio
async def test_topic_to_schema_many_posts() -> None:
    """Test topic with many posts."""
    # Create mock topic
    topic_id = uuid.uuid4()

    # Create mock author
    mock_author = mock.MagicMock()
    mock_author.id = uuid.uuid4()

    # Create mock topic
    topic = mock.MagicMock(spec=Topic)
    topic.id = topic_id
    topic.title = "Test Topic with Many Posts"
    topic.description = "Test topic description"
    topic.author = mock_author
    topic.created_at = datetime.now()
    topic.updated_at = datetime.now()
    topic.topic_tags = []

    # Set up mock methods
    topic.fetch_related = mock.AsyncMock()

    # Mock Post.filter().count() to return a large number
    mock_filter = mock.MagicMock()
    mock_filter.count = mock.AsyncMock(return_value=1000)  # Many posts

    # Create a proper mock UserSchema that matches the expected structure
    from backend.schemas.user import UserSchema

    mock_user_schema = UserSchema(
        id=mock_author.id,
        email="test_author@example.com",
        display_name="Test Author",
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
            "backend.converters.topic_to_schema.user_to_schema",
            mock.AsyncMock(return_value=mock_user_schema),
        ),
    ):
        # Act
        schema = await topic_to_schema(topic)

        # Assert
        assert schema.post_count == 1000
