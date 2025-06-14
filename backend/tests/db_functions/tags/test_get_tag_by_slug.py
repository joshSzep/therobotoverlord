from unittest import mock

import pytest

from backend.db.models.tag import Tag
from backend.db_functions.tags.get_tag_by_slug import get_tag_by_slug
from backend.schemas.tag import TagResponse


@pytest.fixture
def mock_tag() -> mock.MagicMock:
    tag = mock.MagicMock(spec=Tag)
    return tag


@pytest.fixture
def mock_response() -> TagResponse:
    return mock.MagicMock(spec=TagResponse)


@pytest.mark.asyncio
async def test_get_tag_by_slug_success(mock_tag, mock_response) -> None:
    with (
        mock.patch.object(
            Tag, "get_or_none", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.tags.get_tag_by_slug.tag_to_schema",
            new=mock.AsyncMock(return_value=mock_response),
        ) as mock_conv,
    ):
        result = await get_tag_by_slug("slug")
        assert result == mock_response
        mock_get.assert_called_once_with(slug="slug")
        mock_conv.assert_called_once_with(mock_tag)


@pytest.mark.asyncio
async def test_get_tag_by_slug_not_found() -> None:
    with mock.patch.object(
        Tag, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        result = await get_tag_by_slug("missing")
        assert result is None
        mock_get.assert_called_once_with(slug="missing")
