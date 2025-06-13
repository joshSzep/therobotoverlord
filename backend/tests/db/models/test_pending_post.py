from unittest import mock

import pytest

from backend.db.models.pending_post import PendingPost
from backend.db.models.topic import Topic
from backend.db.models.user import User


@pytest.mark.asyncio
async def test_pending_post_create() -> None:
    # Arrange
    content = "Pending content"
    mock_author = mock.AsyncMock(spec=User)
    mock_topic = mock.AsyncMock(spec=Topic)

    # Mock the PendingPost.create method
    with mock.patch.object(PendingPost, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await PendingPost.create(
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
async def test_pending_post_fields() -> None:
    # Arrange
    post = PendingPost(content="Example")

    # Assert
    assert post.content == "Example"
    assert post.parent_post_id is None
