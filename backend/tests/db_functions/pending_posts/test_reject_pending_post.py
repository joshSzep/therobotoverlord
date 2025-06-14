from unittest import mock
import uuid

import pytest

from backend.db.models.pending_post import PendingPost
from backend.db.models.rejected_post import RejectedPost
from backend.db_functions.pending_posts.reject_pending_post import reject_pending_post
from backend.schemas.rejected_post import RejectedPostResponse


@pytest.fixture
def mock_author() -> mock.MagicMock:
    user = mock.MagicMock()
    user.id = uuid.uuid4()
    return user


@pytest.fixture
def mock_topic() -> mock.MagicMock:
    return mock.MagicMock()


@pytest.fixture
def mock_pending_post(mock_author, mock_topic) -> mock.MagicMock:
    pp = mock.MagicMock(spec=PendingPost)
    pp.id = uuid.uuid4()
    pp.content = "hi"

    async def _author():
        return mock_author

    async def _topic():
        return mock_topic

    pp.author = _author()
    pp.topic = _topic()
    pp.parent_post_id = None
    pp.delete = mock.AsyncMock()
    return pp


@pytest.fixture
def mock_rejected_post(mock_author, mock_topic) -> mock.MagicMock:
    rp = mock.MagicMock(spec=RejectedPost)
    rp.id = uuid.uuid4()
    rp.content = "hi"
    rp.author = mock_author
    rp.topic = mock_topic
    return rp


@pytest.fixture
def mock_rejected_response() -> RejectedPostResponse:
    return mock.MagicMock(spec=RejectedPostResponse)


@pytest.mark.asyncio
async def test_reject_pending_post_success(
    mock_pending_post,
    mock_rejected_post,
    mock_rejected_response,
    mock_author,
    mock_topic,
) -> None:
    with (
        mock.patch.object(
            PendingPost,
            "get_or_none",
            new=mock.AsyncMock(return_value=mock_pending_post),
        ) as mock_get,
        mock.patch.object(
            RejectedPost, "create", new=mock.AsyncMock(return_value=mock_rejected_post)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.pending_posts.reject_pending_post.increment_user_rejection_count",
            new=mock.AsyncMock(),
        ) as mock_inc,
        mock.patch(
            "backend.db_functions.pending_posts.reject_pending_post.rejected_post_to_schema",
            new=mock.AsyncMock(return_value=mock_rejected_response),
        ) as mock_conv,
    ):
        result = await reject_pending_post(mock_pending_post.id, "bad")

        assert result == mock_rejected_response
        mock_get.assert_called_once_with(id=mock_pending_post.id)
        mock_create.assert_called_once_with(
            content=mock_pending_post.content,
            author=mock_author,
            topic=mock_topic,
            parent_post_id=mock_pending_post.parent_post_id,
            moderation_reason="bad",
        )
        mock_inc.assert_called_once_with(mock_author.id, mock_rejected_post.id)
        mock_pending_post.delete.assert_called_once()
        mock_conv.assert_called_once_with(mock_rejected_post)


@pytest.mark.asyncio
async def test_reject_pending_post_not_found() -> None:
    with mock.patch.object(
        PendingPost, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        result = await reject_pending_post(uuid.uuid4(), "why")
        assert result is None
        mock_get.assert_called_once()
