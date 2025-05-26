from unittest import mock
import uuid

import pytest

from backend.routes.topics.create_topic import create_topic
from backend.routes.topics.schemas import TopicCreate
from backend.routes.topics.schemas import TopicResponse


@pytest.mark.asyncio
async def test_create_topic_success():
    """Test successful topic creation."""
    # Arrange
    topic_data = TopicCreate(
        title="Test Topic",
        description="Test description",
        tags=["test", "example"],
    )

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.is_verified = True
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = "2025-05-25T00:00:00"
    mock_user.updated_at = "2025-05-25T00:00:00"

    # Create mock topic
    mock_topic = mock.AsyncMock()
    mock_topic.id = uuid.uuid4()
    mock_topic.title = topic_data.title
    mock_topic.description = topic_data.description
    mock_topic.author = mock_user
    mock_topic.created_at = "2025-05-25T00:00:00"
    mock_topic.updated_at = "2025-05-25T00:00:00"
    mock_topic.fetch_related = mock.AsyncMock()

    # Create mock tags
    mock_tags = []
    for tag_name in topic_data.tags:
        mock_tag = mock.AsyncMock()
        mock_tag.id = uuid.uuid4()
        mock_tag.name = tag_name
        mock_tag.slug = tag_name.lower()
        mock_tags.append(mock_tag)

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.create_topic.Topic.create",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.Tag.get_or_create",
            new=mock.AsyncMock(return_value=(mock_tags[0], True)),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.TopicTag.create",
            new=mock.AsyncMock(),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.Tag.get",
            new=mock.AsyncMock(side_effect=mock_tags),
        ),
    ):
        # Act
        result = await create_topic(topic_data, mock_user)

        # Assert
        assert isinstance(result, TopicResponse)
        assert result.title == topic_data.title
        assert result.description == topic_data.description
        assert len(result.tags) == len(topic_data.tags)
        assert result.tags[0].name == topic_data.tags[0]


@pytest.mark.asyncio
async def test_create_topic_with_existing_tags():
    """Test topic creation with existing tags."""
    # Arrange
    topic_data = TopicCreate(
        title="Test Topic",
        description="Test description",
        tags=["existing", "new"],
    )

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.is_verified = True
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = "2025-05-25T00:00:00"
    mock_user.updated_at = "2025-05-25T00:00:00"

    # Create mock topic
    mock_topic = mock.AsyncMock()
    mock_topic.id = uuid.uuid4()
    mock_topic.title = topic_data.title
    mock_topic.description = topic_data.description
    mock_topic.author = mock_user
    mock_topic.created_at = "2025-05-25T00:00:00"
    mock_topic.updated_at = "2025-05-25T00:00:00"
    mock_topic.fetch_related = mock.AsyncMock()

    # Create mock tags
    mock_existing_tag = mock.AsyncMock()
    mock_existing_tag.id = uuid.uuid4()
    mock_existing_tag.name = "existing"
    mock_existing_tag.slug = "existing"

    mock_new_tag = mock.AsyncMock()
    mock_new_tag.id = uuid.uuid4()
    mock_new_tag.name = "new"
    mock_new_tag.slug = "new"

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.create_topic.Topic.create",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.Tag.get_or_create",
            new=mock.AsyncMock(
                side_effect=[
                    (mock_existing_tag, False),  # Existing tag
                    (mock_new_tag, True),  # New tag
                ]
            ),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.TopicTag.create",
            new=mock.AsyncMock(),
        ),
        mock.patch(
            "backend.routes.topics.create_topic.Tag.get",
            new=mock.AsyncMock(side_effect=[mock_existing_tag, mock_new_tag]),
        ),
    ):
        # Act
        result = await create_topic(topic_data, mock_user)

        # Assert
        assert isinstance(result, TopicResponse)
        assert result.title == topic_data.title
        assert result.description == topic_data.description
        assert len(result.tags) == len(topic_data.tags)
        assert result.tags[0].name == "existing"
        assert result.tags[1].name == "new"


@pytest.mark.asyncio
async def test_create_topic_without_tags():
    """Test topic creation without any tags."""
    # Arrange
    topic_data = TopicCreate(
        title="Test Topic",
        description="Test description",
        tags=[],
    )

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.is_verified = True
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = "2025-05-25T00:00:00"
    mock_user.updated_at = "2025-05-25T00:00:00"

    # Create mock topic
    mock_topic = mock.AsyncMock()
    mock_topic.id = uuid.uuid4()
    mock_topic.title = topic_data.title
    mock_topic.description = topic_data.description
    mock_topic.author = mock_user
    mock_topic.created_at = "2025-05-25T00:00:00"
    mock_topic.updated_at = "2025-05-25T00:00:00"
    mock_topic.fetch_related = mock.AsyncMock()

    # Mock dependencies
    with mock.patch(
        "backend.routes.topics.create_topic.Topic.create",
        new=mock.AsyncMock(return_value=mock_topic),
    ):
        # Act
        result = await create_topic(topic_data, mock_user)

        # Assert
        assert isinstance(result, TopicResponse)
        assert result.title == topic_data.title
        assert result.description == topic_data.description
        assert len(result.tags) == 0
