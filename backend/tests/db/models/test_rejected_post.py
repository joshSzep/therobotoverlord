from unittest import mock

import pytest

from backend.db.models.rejected_post import RejectedPost
from backend.db.models.topic import Topic
from backend.db.models.user import User


@pytest.mark.asyncio
async def test_rejected_post_create() -> None:
    # Arrange
    content = "Rejected"
    reason = "Spam"
    mock_author = mock.AsyncMock(spec=User)
    mock_topic = mock.AsyncMock(spec=Topic)

    # Mock the RejectedPost.create method
    with mock.patch.object(RejectedPost, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await RejectedPost.create(
            content=content,
            author=mock_author,
            topic=mock_topic,
            moderation_reason=reason,
        )

        # Assert
        mock_create.assert_called_once_with(
            content=content,
            author=mock_author,
            topic=mock_topic,
            moderation_reason=reason,
        )


@pytest.mark.asyncio
async def test_rejected_post_fields() -> None:
    # Arrange
    post = RejectedPost(content="Text", moderation_reason="Spam")

    # Assert
    assert post.content == "Text"
    assert post.moderation_reason == "Spam"
    assert post.parent_post_id is None
