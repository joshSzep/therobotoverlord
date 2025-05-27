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
