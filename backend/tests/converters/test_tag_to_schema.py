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


@pytest.mark.asyncio
async def test_tag_to_schema_missing_id() -> None:
    """Test error handling when tag has no id."""
    # Create mock tag without an id
    tag = mock.MagicMock(spec=Tag)
    tag.name = "Test Tag"
    tag.slug = "test-tag"

    # The id attribute is missing
    delattr(tag, "id")

    # Act and Assert
    with pytest.raises(AttributeError):
        await tag_to_schema(tag)


@pytest.mark.asyncio
async def test_tag_to_schema_missing_name() -> None:
    """Test error handling when tag has no name."""
    # Create mock tag without a name
    tag = mock.MagicMock(spec=Tag)
    tag.id = uuid.uuid4()
    tag.slug = "test-tag"

    # The name attribute is missing
    delattr(tag, "name")

    # Act and Assert
    with pytest.raises(AttributeError):
        await tag_to_schema(tag)


@pytest.mark.asyncio
async def test_tag_to_schema_missing_slug() -> None:
    """Test error handling when tag has no slug."""
    # Create mock tag without a slug
    tag = mock.MagicMock(spec=Tag)
    tag.id = uuid.uuid4()
    tag.name = "Test Tag"

    # The slug attribute is missing
    delattr(tag, "slug")

    # Act and Assert
    with pytest.raises(AttributeError):
        await tag_to_schema(tag)


@pytest.mark.asyncio
async def test_tag_to_schema_none_input() -> None:
    """Test error handling when tag is None."""
    # Act and Assert
    with pytest.raises(AttributeError):
        await tag_to_schema(None)
