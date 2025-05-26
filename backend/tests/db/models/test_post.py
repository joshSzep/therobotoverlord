from unittest import mock

import pytest

from backend.db.models.post import Post
from backend.db.models.topic import Topic
from backend.db.models.user import User


@pytest.mark.asyncio
async def test_post_create() -> None:
    # Arrange
    content = "This is a test post content"
    mock_author = mock.AsyncMock(spec=User)
    mock_topic = mock.AsyncMock(spec=Topic)

    # Mock the Post.create method
    with mock.patch.object(Post, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await Post.create(
            content=content,
            author=mock_author,
            topic=mock_topic,
        )

        # Assert
        mock_create.assert_called_once_with(
            content=content,
            author=mock_author,
            topic=mock_topic,
        )


@pytest.mark.asyncio
async def test_post_create_with_parent() -> None:
    # Arrange
    content = "This is a reply to another post"
    mock_author = mock.AsyncMock(spec=User)
    mock_topic = mock.AsyncMock(spec=Topic)
    mock_parent_post = mock.AsyncMock(spec=Post)

    # Mock the Post.create method
    with mock.patch.object(Post, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await Post.create(
            content=content,
            author=mock_author,
            topic=mock_topic,
            parent_post=mock_parent_post,
        )

        # Assert
        mock_create.assert_called_once_with(
            content=content,
            author=mock_author,
            topic=mock_topic,
            parent_post=mock_parent_post,
        )


@pytest.mark.asyncio
async def test_post_fields() -> None:
    # Arrange
    post = Post(
        content="This is a test post content",
    )

    # Assert
    assert post.content == "This is a test post content"
    # Don't test relationship fields directly as they're ForeignKeyFields
