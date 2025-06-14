from unittest import mock

import pytest

from backend.db.models.tag import Tag
from backend.db_functions.tags.get_or_create_tag_by_name import (
    get_or_create_tag_by_name,
)
from backend.schemas.tag import TagResponse


@pytest.fixture
def existing_tag() -> TagResponse:
    return mock.MagicMock(spec=TagResponse)


@pytest.mark.asyncio
async def test_get_or_create_tag_by_name_existing(existing_tag) -> None:
    with mock.patch(
        "backend.db_functions.tags.get_or_create_tag_by_name.get_tag_by_name",
        new=mock.AsyncMock(return_value=existing_tag),
    ) as mock_get:
        result = await get_or_create_tag_by_name("name")
        assert result == existing_tag
        mock_get.assert_called_once_with("name")


@pytest.mark.asyncio
async def test_get_or_create_tag_by_name_creates_new() -> None:
    tag_model = mock.MagicMock(spec=Tag)
    created = mock.MagicMock(spec=TagResponse)
    with (
        mock.patch(
            "backend.db_functions.tags.get_or_create_tag_by_name.get_tag_by_name",
            new=mock.AsyncMock(return_value=None),
        ) as mock_get,
        mock.patch.object(
            Tag, "create", new=mock.AsyncMock(return_value=tag_model)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.tags.get_or_create_tag_by_name.tag_to_schema",
            new=mock.AsyncMock(return_value=created),
        ) as mock_conv,
    ):
        result = await get_or_create_tag_by_name("My Tag")
        assert result == created
        mock_get.assert_called_once_with("My Tag")
        mock_create.assert_called_once()
        mock_conv.assert_called_once_with(tag_model)
