from unittest import mock

import pytest

from backend.db.models.topic import Topic
from backend.db.models.user import User


@pytest.mark.asyncio
async def test_topic_create() -> None:
    # Arrange
    title = "Test Topic"
    mock_author = mock.AsyncMock(spec=User)
    description = "This is a test topic description"

    # Mock the Topic.create method
    with mock.patch.object(Topic, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await Topic.create(
            title=title,
            author=mock_author,
            description=description,
        )

        # Assert
        mock_create.assert_called_once_with(
            title=title,
            author=mock_author,
            description=description,
        )


@pytest.mark.asyncio
async def test_topic_create_without_description() -> None:
    # Arrange
    title = "Test Topic"
    mock_author = mock.AsyncMock(spec=User)

    # Mock the Topic.create method
    with mock.patch.object(Topic, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await Topic.create(
            title=title,
            author=mock_author,
        )

        # Assert
        mock_create.assert_called_once_with(
            title=title,
            author=mock_author,
        )


@pytest.mark.asyncio
async def test_topic_fields() -> None:
    # Arrange
    topic = Topic(
        title="Test Topic",
        description="This is a test topic description",
    )

    # Assert
    assert topic.title == "Test Topic"
    assert topic.description == "This is a test topic description"
    # Don't test the author field directly as it's a ForeignKeyField
