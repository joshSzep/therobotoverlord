from unittest import mock
import uuid

import pytest

from backend.db.models.pending_post import PendingPost
from backend.db_functions.pending_posts.list_pending_posts_by_topic import (
    list_pending_posts_by_topic,
)
from backend.schemas.pending_post import PendingPostResponse


@pytest.fixture
def mock_pending_posts() -> list[mock.MagicMock]:
    posts = []
    for _ in range(3):
        p = mock.MagicMock(spec=PendingPost)
        posts.append(p)
    return posts


@pytest.fixture
def mock_responses(mock_pending_posts) -> list[PendingPostResponse]:
    return [mock.MagicMock(spec=PendingPostResponse) for _ in mock_pending_posts]


@pytest.mark.asyncio
async def test_list_pending_posts_by_topic_success(
    mock_pending_posts, mock_responses
) -> None:
    qs = mock.MagicMock()
    qs.order_by.return_value.all = mock.AsyncMock(return_value=mock_pending_posts)
    with (
        mock.patch.object(PendingPost, "filter", return_value=qs) as mock_filter,
        mock.patch(
            "backend.db_functions.pending_posts.list_pending_posts_by_topic.pending_post_to_schema",
            new=mock.AsyncMock(side_effect=mock_responses),
        ) as mock_conv,
    ):
        topic_id = uuid.uuid4()
        result = await list_pending_posts_by_topic(topic_id)
        assert len(result) == len(mock_pending_posts)
        mock_filter.assert_called_once_with(topic_id=topic_id)
        qs.order_by.assert_called_once_with("-created_at")
        qs.order_by.return_value.all.assert_called_once()
        assert mock_conv.call_count == len(mock_pending_posts)


@pytest.mark.asyncio
async def test_list_pending_posts_by_topic_error() -> None:
    with mock.patch.object(
        PendingPost, "filter", side_effect=Exception("db")
    ) as mock_filter:
        result = await list_pending_posts_by_topic(uuid.uuid4())
        assert result == []
        mock_filter.assert_called_once()
