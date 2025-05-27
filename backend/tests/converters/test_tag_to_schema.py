from datetime import datetime
from unittest import mock
import uuid

import pytest

from backend.converters.tag_to_schema import tag_to_schema
from backend.db.models.tag import Tag
from backend.schemas.tag import TagResponse


@pytest.fixture
def mock_tag() -> mock.MagicMock:
    tag_id = uuid.uuid4()

    # Create mock tag
    tag = mock.MagicMock(spec=Tag)
    tag.id = tag_id
    tag.name = "Test Tag"
    tag.slug = "test-tag"
    tag.created_at = datetime.now()
    tag.updated_at = datetime.now()

    return tag


@pytest.mark.asyncio
async def test_tag_to_schema(mock_tag) -> None:
    # Convert the mock tag to a schema
    schema = await tag_to_schema(mock_tag)

    # Verify the schema has the correct values
    assert isinstance(schema, TagResponse)
    assert schema.id == mock_tag.id
    assert schema.name == mock_tag.name
    assert schema.slug == mock_tag.slug
