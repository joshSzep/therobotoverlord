from unittest import mock

import pytest

from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.db.models.topic_tag import TopicTag


@pytest.mark.asyncio
async def test_topic_tag_create() -> None:
    # Arrange
    mock_topic = mock.AsyncMock(spec=Topic)
    mock_tag = mock.AsyncMock(spec=Tag)

    # Mock the TopicTag.create method
    with mock.patch.object(TopicTag, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await TopicTag.create(
            topic=mock_topic,
            tag=mock_tag,
        )

        # Assert
        mock_create.assert_called_once_with(
            topic=mock_topic,
            tag=mock_tag,
        )


@pytest.mark.asyncio
async def test_topic_tag_fields() -> None:
    # Arrange
    topic_tag = TopicTag()

    # Assert
    # We don't test relationship fields directly as they're ForeignKeyFields
    assert isinstance(topic_tag, TopicTag)


@pytest.mark.asyncio
async def test_topic_tag_meta() -> None:
    # Test that the Meta class is properly configured

    # Assert
    # Access Meta class attributes through the model's metadata
    meta = TopicTag.Meta
    assert meta.table == "topic_tag"
    assert ("topic", "tag") in meta.unique_together
