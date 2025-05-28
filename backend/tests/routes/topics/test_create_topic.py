# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
import pytest

# Project-specific imports
from backend.routes.topics.create_topic import create_topic
from backend.schemas.topic import TopicCreate
from backend.schemas.topic import TopicResponse


@pytest.mark.asyncio
async def test_create_topic_success():
    """Test successful topic creation."""
    # Arrange
    user_id = uuid.uuid4()
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.is_verified = True
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = datetime(2025, 5, 25)
    mock_user.updated_at = datetime(2025, 5, 25)

    # Create topic data
    topic_data = TopicCreate(
        title="Test Topic", description="This is a test topic", tags=["test-tag"]
    )

    # Create mock topic
    mock_topic = mock.AsyncMock()
    mock_topic.id = topic_id
    mock_topic.title = topic_data.title
    mock_topic.description = topic_data.description
    mock_topic.created_by_id = user_id
    mock_topic.created_at = datetime(2025, 5, 25)
    mock_topic.updated_at = datetime(2025, 5, 25)

    # Create mock tag
    mock_tag = mock.AsyncMock()
    mock_tag.id = tag_id
    mock_tag.name = "test-tag"
    mock_tag.slug = "test-tag"

    # No need to create expected response objects as we'll compare individual fields

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.create_topic.db_create_topic",
            new=mock.AsyncMock(return_value=mock_topic),
        ) as mock_db_create_topic,
        mock.patch(
            "backend.routes.topics.create_topic.get_tag_by_slug",
            new=mock.AsyncMock(return_value=None),
        ) as mock_get_tag_by_slug,
        mock.patch(
            "backend.routes.topics.create_topic.create_tag",
            new=mock.AsyncMock(return_value=mock_tag),
        ) as mock_create_tag,
        mock.patch(
            "backend.routes.topics.create_topic.add_tags_to_topic",
            new=mock.AsyncMock(),
        ) as mock_add_tags_to_topic,
        mock.patch(
            "backend.routes.topics.create_topic.get_tags_for_topic",
            new=mock.AsyncMock(return_value=[mock_tag]),
        ) as mock_get_tags_for_topic,
        mock.patch(
            "backend.routes.topics.create_topic.slugify",
            return_value="test-tag",
        ) as mock_slugify,
    ):
        # Act
        result = await create_topic(
            topic_data=topic_data,
            current_user=mock_user,
        )

        # Assert
        assert isinstance(result, TopicResponse)
        assert result.id == topic_id
        assert result.title == topic_data.title
        assert result.description == topic_data.description
        assert result.author.id == user_id
        assert len(result.tags) == 1
        assert result.tags[0].id == tag_id
        assert result.tags[0].name == "test-tag"
        assert result.tags[0].slug == "test-tag"

        # Verify function calls
        mock_db_create_topic.assert_called_once_with(
            title=topic_data.title,
            description=topic_data.description,
            created_by_id=user_id,
        )
        mock_get_tag_by_slug.assert_called_once_with("test-tag")
        mock_create_tag.assert_called_once_with("test-tag", "test-tag")
        mock_add_tags_to_topic.assert_called_once_with(topic_id, [tag_id])
        mock_get_tags_for_topic.assert_called_once_with(topic_id)
        mock_slugify.assert_called_with("test-tag")


@pytest.mark.asyncio
async def test_create_topic_with_existing_tag():
    """Test topic creation with an existing tag."""
    # Arrange
    user_id = uuid.uuid4()
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.is_verified = True
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = datetime(2025, 5, 25)
    mock_user.updated_at = datetime(2025, 5, 25)

    # Create topic data
    topic_data = TopicCreate(
        title="Test Topic", description="This is a test topic", tags=["existing-tag"]
    )

    # Create mock topic
    mock_topic = mock.AsyncMock()
    mock_topic.id = topic_id
    mock_topic.title = topic_data.title
    mock_topic.description = topic_data.description
    mock_topic.created_by_id = user_id
    mock_topic.created_at = datetime(2025, 5, 25)
    mock_topic.updated_at = datetime(2025, 5, 25)

    # Create mock tag (existing)
    mock_tag = mock.AsyncMock()
    mock_tag.id = tag_id
    mock_tag.name = "existing-tag"
    mock_tag.slug = "existing-tag"

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.create_topic.db_create_topic",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.get_tag_by_slug",
            new=mock.AsyncMock(return_value=mock_tag),
        ) as mock_get_tag_by_slug,
        mock.patch(
            "backend.routes.topics.create_topic.create_tag",
            new=mock.AsyncMock(),
        ) as mock_create_tag,
        mock.patch(
            "backend.routes.topics.create_topic.add_tags_to_topic",
            new=mock.AsyncMock(),
        ) as mock_add_tags_to_topic,
        mock.patch(
            "backend.routes.topics.create_topic.get_tags_for_topic",
            new=mock.AsyncMock(return_value=[mock_tag]),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.slugify",
            return_value="existing-tag",
        ),
    ):
        # Act
        result = await create_topic(
            topic_data=topic_data,
            current_user=mock_user,
        )

        # Assert
        assert isinstance(result, TopicResponse)
        assert result.id == topic_id
        assert len(result.tags) == 1
        assert result.tags[0].id == tag_id

        # Verify function calls
        mock_get_tag_by_slug.assert_called_once_with("existing-tag")
        mock_create_tag.assert_not_called()  # Should not create a new tag
        mock_add_tags_to_topic.assert_called_once_with(topic_id, [tag_id])


@pytest.mark.asyncio
async def test_create_topic_with_tag_error():
    """Test topic creation with an error during tag processing."""
    # Arrange
    user_id = uuid.uuid4()
    topic_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.is_verified = True
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = datetime(2025, 5, 25)
    mock_user.updated_at = datetime(2025, 5, 25)

    # Create topic data
    topic_data = TopicCreate(
        title="Test Topic", description="This is a test topic", tags=["test-tag"]
    )

    # Create mock topic
    mock_topic = mock.AsyncMock()
    mock_topic.id = topic_id
    mock_topic.title = topic_data.title
    mock_topic.description = topic_data.description
    mock_topic.created_by_id = user_id
    mock_topic.created_at = datetime(2025, 5, 25)
    mock_topic.updated_at = datetime(2025, 5, 25)

    # Create mock tag
    mock_tag = mock.AsyncMock()
    mock_tag.id = uuid.uuid4()
    mock_tag.name = "test-tag"
    mock_tag.slug = "test-tag"

    # Mock dependencies with error in add_tags_to_topic
    with (
        mock.patch(
            "backend.routes.topics.create_topic.db_create_topic",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.get_tag_by_slug",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.create_tag",
            new=mock.AsyncMock(return_value=mock_tag),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.add_tags_to_topic",
            new=mock.AsyncMock(side_effect=Exception("Tag error")),
        ) as mock_add_tags_to_topic,
        mock.patch(
            "backend.routes.topics.create_topic.get_tags_for_topic",
            new=mock.AsyncMock(return_value=[]),
        ) as mock_get_tags_for_topic,
        mock.patch(
            "backend.routes.topics.create_topic.slugify",
            return_value="test-tag",
        ),
        mock.patch(
            "builtins.print",
        ) as mock_print,
    ):
        # Act
        result = await create_topic(
            topic_data=topic_data,
            current_user=mock_user,
        )

        # Assert
        assert isinstance(result, TopicResponse)
        assert result.id == topic_id
        assert len(result.tags) == 0  # No tags due to error

        # Verify error was logged
        mock_print.assert_called_once()
        assert "Error creating topic-tag relationships" in mock_print.call_args[0][0]

        # Verify function calls
        mock_add_tags_to_topic.assert_called_once()
        mock_get_tags_for_topic.assert_called_once_with(topic_id)
