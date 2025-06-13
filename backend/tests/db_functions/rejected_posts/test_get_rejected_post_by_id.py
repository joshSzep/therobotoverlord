from unittest import mock
import uuid

import pytest

from backend.db.models.rejected_post import RejectedPost
from backend.db_functions.rejected_posts.get_rejected_post_by_id import (
    get_rejected_post_by_id,
)
from backend.schemas.rejected_post import RejectedPostResponse


@pytest.fixture
def mock_rejected_post() -> mock.MagicMock:
    rp = mock.MagicMock(spec=RejectedPost)
    rp.id = uuid.uuid4()
    return rp


@pytest.fixture
def mock_response() -> RejectedPostResponse:
    return mock.MagicMock(spec=RejectedPostResponse)


@pytest.mark.asyncio
async def test_get_rejected_post_by_id_success(
    mock_rejected_post, mock_response
) -> None:
    with (
        mock.patch.object(
            RejectedPost,
            "get_or_none",
            new=mock.AsyncMock(return_value=mock_rejected_post),
        ) as mock_get,
        mock.patch(
            "backend.db_functions.rejected_posts.get_rejected_post_by_id.rejected_post_to_schema",
            new=mock.AsyncMock(return_value=mock_response),
        ) as mock_conv,
    ):
        result = await get_rejected_post_by_id(mock_rejected_post.id)
        assert result == mock_response
        mock_get.assert_called_once_with(id=mock_rejected_post.id)
        mock_conv.assert_called_once_with(mock_rejected_post)


@pytest.mark.asyncio
async def test_get_rejected_post_by_id_not_found() -> None:
    with mock.patch.object(
        RejectedPost, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        result = await get_rejected_post_by_id(uuid.uuid4())
        assert result is None
        mock_get.assert_called_once()
