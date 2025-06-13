from unittest import mock
import uuid

import pytest

from backend.db.models.pending_post import PendingPost
from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.schemas.pending_post import PendingPostResponse


@pytest.fixture
def mock_pending_post() -> mock.MagicMock:
    pp = mock.MagicMock(spec=PendingPost)
    pp.id = uuid.uuid4()
    return pp


@pytest.fixture
def mock_pending_post_response() -> PendingPostResponse:
    return mock.MagicMock(spec=PendingPostResponse)


@pytest.mark.asyncio
async def test_get_pending_post_by_id_success(
    mock_pending_post, mock_pending_post_response
) -> None:
    with (
        mock.patch.object(
            PendingPost,
            "get_or_none",
            new=mock.AsyncMock(return_value=mock_pending_post),
        ) as mock_get,
        mock.patch(
            "backend.db_functions.pending_posts.get_pending_post_by_id.pending_post_to_schema",
            new=mock.AsyncMock(return_value=mock_pending_post_response),
        ) as mock_conv,
    ):
        result = await get_pending_post_by_id(mock_pending_post.id)

        assert result == mock_pending_post_response
        mock_get.assert_called_once_with(id=mock_pending_post.id)
        mock_conv.assert_called_once_with(mock_pending_post)


@pytest.mark.asyncio
async def test_get_pending_post_by_id_not_found() -> None:
    with mock.patch.object(
        PendingPost, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        result = await get_pending_post_by_id(uuid.uuid4())
        assert result is None
        mock_get.assert_called_once()
