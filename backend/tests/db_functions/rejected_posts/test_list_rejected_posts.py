from unittest import mock
import uuid

import pytest

from backend.db.models.rejected_post import RejectedPost
from backend.db_functions.rejected_posts.list_rejected_posts import list_rejected_posts
from backend.schemas.rejected_post import RejectedPostList
from backend.schemas.rejected_post import RejectedPostResponse


@pytest.fixture
def mock_rejected_posts() -> list[mock.MagicMock]:
    return [mock.MagicMock(spec=RejectedPost) for _ in range(3)]


@pytest.fixture
def mock_responses(mock_rejected_posts) -> list[RejectedPostResponse]:
    return [mock.MagicMock(spec=RejectedPostResponse) for _ in mock_rejected_posts]


@pytest.mark.asyncio
async def test_list_rejected_posts_success(mock_rejected_posts, mock_responses) -> None:
    qs = mock.MagicMock()
    qs.order_by.return_value.offset.return_value.limit = mock.AsyncMock(
        return_value=mock_rejected_posts
    )
    qs.order_by.return_value.offset.return_value.limit.__name__ = (
        "limit"  # for assert? but not needed
    )
    with (
        mock.patch.object(RejectedPost, "all", return_value=qs) as mock_all,
        mock.patch(
            "backend.db_functions.rejected_posts.list_rejected_posts.rejected_post_to_schema",
            new=mock.AsyncMock(side_effect=mock_responses),
        ) as mock_conv,
    ):
        qs.count = mock.AsyncMock(return_value=len(mock_rejected_posts))
        result = await list_rejected_posts(limit=5, offset=0)
        assert isinstance(result, RejectedPostList)
        assert result.count == len(mock_rejected_posts)
        mock_all.assert_called_once()
        qs.order_by.assert_called_once_with("-created_at")
        qs.order_by.return_value.offset.assert_called_once_with(0)
        qs.order_by.return_value.offset.return_value.limit.assert_called_once_with(5)
        assert mock_conv.call_count == len(mock_rejected_posts)


@pytest.mark.asyncio
async def test_list_rejected_posts_filtered(mock_rejected_posts) -> None:
    qs = mock.MagicMock()
    qs.order_by.return_value.offset.return_value.limit = mock.AsyncMock(
        return_value=mock_rejected_posts
    )
    qs.count = mock.AsyncMock(return_value=1)
    with (
        mock.patch.object(RejectedPost, "all", return_value=qs) as mock_all,
        mock.patch.object(qs, "filter", return_value=qs) as mock_filter,
        mock.patch(
            "backend.db_functions.rejected_posts.list_rejected_posts.rejected_post_to_schema",
            new=mock.AsyncMock(return_value=mock.MagicMock(spec=RejectedPostResponse)),
        ),
    ):
        user = uuid.uuid4()
        await list_rejected_posts(user_id=user)
        mock_all.assert_called_once()
        mock_filter.assert_called_once_with(user_id=user)
