from unittest import mock
import uuid

import pytest

from backend.db.models.post import Post
from backend.db_functions.posts.list_posts_by_user import list_posts_by_user
from backend.schemas.post import PostResponse


@pytest.fixture
def mock_posts() -> list[mock.MagicMock]:
    return [mock.MagicMock(spec=Post) for _ in range(3)]


@pytest.fixture
def mock_responses(mock_posts) -> list[PostResponse]:
    return [mock.MagicMock(spec=PostResponse) for _ in mock_posts]


@pytest.mark.asyncio
async def test_list_posts_by_user_success(mock_posts, mock_responses) -> None:
    qs = mock.MagicMock()
    qs.order_by.return_value.offset.return_value.limit.return_value.all = (
        mock.AsyncMock(return_value=mock_posts)
    )
    with (
        mock.patch.object(Post, "filter", return_value=qs) as mock_filter,
        mock.patch(
            "backend.db_functions.posts.list_posts_by_user.post_to_schema",
            new=mock.AsyncMock(side_effect=mock_responses),
        ) as mock_conv,
    ):
        user = uuid.uuid4()
        result = await list_posts_by_user(user)
        mock_filter.assert_called_once_with(author_id=user)
        qs.order_by.assert_called_once_with("-created_at")
        qs.order_by.return_value.offset.assert_called_once_with(0)
        qs.order_by.return_value.offset.return_value.limit.assert_called_once_with(10)
        qs.order_by.return_value.offset.return_value.limit.return_value.all.assert_called_once()
        assert len(result) == len(mock_posts)
        assert mock_conv.call_count == len(mock_posts)


@pytest.mark.asyncio
async def test_list_posts_by_user_count_only() -> None:
    qs = mock.MagicMock()
    qs.count = mock.AsyncMock(return_value=4)
    with mock.patch.object(Post, "filter", return_value=qs) as mock_filter:
        user = uuid.uuid4()
        result = await list_posts_by_user(user, count_only=True)
        assert result == 4
        mock_filter.assert_called_once_with(author_id=user)
        qs.count.assert_called_once()
