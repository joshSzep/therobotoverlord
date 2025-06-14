from unittest import mock

import pytest

from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.db_functions.topics.list_topics_by_tag_slug import list_topics_by_tag_slug
from backend.schemas.topic import TopicList
from backend.schemas.topic import TopicResponse


@pytest.fixture
def mock_tag() -> mock.MagicMock:
    tag = mock.MagicMock(spec=Tag)
    tag.id = 1
    return tag


@pytest.fixture
def mock_topics() -> list[mock.MagicMock]:
    return [mock.MagicMock(spec=Topic) for _ in range(2)]


@pytest.fixture
def mock_responses(mock_topics) -> list[TopicResponse]:
    return [mock.MagicMock(spec=TopicResponse) for _ in mock_topics]


@pytest.mark.asyncio
async def test_list_topics_by_tag_slug_success(
    mock_tag, mock_topics, mock_responses
) -> None:
    qs = mock.MagicMock()
    qs.offset.return_value.limit.return_value.prefetch_related = mock.AsyncMock(
        return_value=mock_topics
    )
    qs.count = mock.AsyncMock(return_value=len(mock_topics))
    with (
        mock.patch.object(
            Tag, "get_or_none", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_get_tag,
        mock.patch.object(Topic, "filter", return_value=qs) as mock_filter,
        mock.patch(
            "backend.db_functions.topics.list_topics_by_tag_slug.topic_to_schema",
            new=mock.AsyncMock(side_effect=mock_responses),
        ) as mock_conv,
    ):
        result = await list_topics_by_tag_slug("tag")
        assert isinstance(result, TopicList)
        assert result.count == len(mock_topics)
        mock_get_tag.assert_called_once_with(slug="tag")
        mock_filter.assert_called_with(topic_tags__tag_id=mock_tag.id)
        qs.offset.assert_called_once_with(0)
        qs.offset.return_value.limit.assert_called_once_with(20)
        qs.offset.return_value.limit.return_value.prefetch_related.assert_called_once_with(
            "author"
        )
        assert mock_conv.call_count == len(mock_topics)


@pytest.mark.asyncio
async def test_list_topics_by_tag_slug_no_tag() -> None:
    with mock.patch.object(
        Tag, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        result = await list_topics_by_tag_slug("unknown")
        assert result.count == 0
        assert result.topics == []
        mock_get.assert_called_once_with(slug="unknown")
