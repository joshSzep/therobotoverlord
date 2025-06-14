from unittest import mock
import uuid

import pytest

from backend.db.models.pending_post import PendingPost
from backend.db.models.post import Post
from backend.db_functions.pending_posts.approve_and_create_post import (
    approve_and_create_post,
)
from backend.schemas.post import PostResponse


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
def mock_post(mock_topic, mock_author) -> mock.MagicMock:
    post = mock.MagicMock(spec=Post)
    post.id = uuid.uuid4()
    post.content = "hi"
    post.author = mock_author
    post.topic = mock_topic
    return post


@pytest.fixture
def mock_post_response() -> PostResponse:
    return mock.MagicMock(spec=PostResponse)


@pytest.mark.asyncio
async def test_approve_and_create_post_success(
    mock_pending_post, mock_post, mock_post_response, mock_author, mock_topic
) -> None:
    with (
        mock.patch.object(
            PendingPost,
            "get_or_none",
            new=mock.AsyncMock(return_value=mock_pending_post),
        ) as mock_get,
        mock.patch.object(
            Post, "create", new=mock.AsyncMock(return_value=mock_post)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.pending_posts.approve_and_create_post.increment_user_approval_count",
            new=mock.AsyncMock(),
        ) as mock_inc,
        mock.patch(
            "backend.db_functions.pending_posts.approve_and_create_post.create_post_approval_event",
            new=mock.AsyncMock(return_value=mock.MagicMock()),
        ) as mock_event,
        mock.patch(
            "backend.db_functions.pending_posts.approve_and_create_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_post_response),
        ) as mock_get_post,
    ):
        result = await approve_and_create_post(mock_pending_post.id)

        assert result == mock_post_response
        mock_get.assert_called_once_with(id=mock_pending_post.id)
        mock_create.assert_called_once_with(
            content=mock_pending_post.content,
            author=mock_author,
            topic=mock_topic,
            parent_post_id=mock_pending_post.parent_post_id,
        )
        mock_inc.assert_called_once_with(mock_author.id, mock_post.id)
        mock_event.assert_called_once_with(
            user_id=mock_author.id,
            pending_post_id=mock_pending_post.id,
            approved_post_id=mock_post.id,
        )
        mock_pending_post.delete.assert_called_once()
        mock_get_post.assert_called_once_with(mock_post.id)


@pytest.mark.asyncio
async def test_approve_and_create_post_not_found() -> None:
    with mock.patch.object(
        PendingPost, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        result = await approve_and_create_post(uuid.uuid4())
        assert result is None
        mock_get.assert_called_once()
