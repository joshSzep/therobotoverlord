from unittest import mock
import uuid

import pytest

from backend.db.models.post import Post
from backend.db_functions.posts.list_posts_by_topic import list_posts_by_topic
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse


@pytest.fixture
def mock_posts() -> list[mock.MagicMock]:
    return [mock.MagicMock(spec=Post) for _ in range(2)]


@pytest.fixture
def mock_responses(mock_posts) -> list[PostResponse]:
    return [mock.MagicMock(spec=PostResponse) for _ in mock_posts]


@pytest.mark.asyncio
async def test_list_posts_by_topic_success(mock_posts, mock_responses) -> None:
    qs = mock.MagicMock()
    qs.offset.return_value.limit.return_value.order_by = mock.AsyncMock(
        return_value=mock_posts
    )
    qs.count = mock.AsyncMock(return_value=len(mock_posts))
    with (
        mock.patch.object(Post, "filter", return_value=qs) as mock_filter,
        mock.patch(
            "backend.db_functions.posts.list_posts_by_topic.post_to_schema",
            new=mock.AsyncMock(side_effect=mock_responses),
        ) as mock_conv,
    ):
        topic_id = uuid.uuid4()
        result = await list_posts_by_topic(topic_id)
        assert isinstance(result, PostList)
        assert result.count == len(mock_posts)
        mock_filter.assert_called_once_with(topic_id=topic_id, parent_post_id=None)
        qs.offset.assert_called_once_with(0)
        qs.offset.return_value.limit.assert_called_once_with(20)
        qs.offset.return_value.limit.return_value.order_by.assert_called_once_with(
            "-created_at"
        )
        assert mock_conv.call_count == len(mock_posts)
