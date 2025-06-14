from unittest import mock
import uuid

import pytest

from backend.db.models.pending_post import PendingPost
from backend.db.models.post import Post
from backend.db.models.rejected_post import RejectedPost
from backend.db.models.user import User
from backend.db_functions.user_stats.get_user_stats import get_user_stats
from backend.schemas.user_stats import UserStatsResponse


@pytest.fixture
def mock_user() -> mock.MagicMock:
    user = mock.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.display_name = "tester"
    return user


@pytest.mark.asyncio
async def test_get_user_stats_success(mock_user) -> None:
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch.object(
            Post, "filter", return_value=mock.MagicMock()
        ) as mock_post_filter,
        mock.patch.object(
            RejectedPost, "filter", return_value=mock.MagicMock()
        ) as mock_rejected_filter,
        mock.patch.object(
            PendingPost, "filter", return_value=mock.MagicMock()
        ) as mock_pending_filter,
    ):
        mock_post_filter.return_value.count = mock.AsyncMock(return_value=5)
        mock_rejected_filter.return_value.count = mock.AsyncMock(return_value=2)
        mock_pending_filter.return_value.count = mock.AsyncMock(return_value=1)
        result = await get_user_stats(mock_user.id)

        assert isinstance(result, UserStatsResponse)
        assert result.approved_count == 5
        assert result.rejected_count == 2
        assert result.pending_count == 1
        assert result.approval_rate == pytest.approx(5 / 7 * 100)
        mock_get.assert_called_once_with(id=mock_user.id)
        mock_post_filter.assert_called_once_with(author_id=mock_user.id)
        mock_rejected_filter.assert_called_once_with(author_id=mock_user.id)
        mock_pending_filter.assert_called_once_with(author_id=mock_user.id)


@pytest.mark.asyncio
async def test_get_user_stats_user_not_found() -> None:
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        with pytest.raises(ValueError):
            await get_user_stats(uuid.uuid4())
        mock_get.assert_called_once()
