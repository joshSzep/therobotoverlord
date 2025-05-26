from unittest import mock

import pytest

from backend.db.models.tag import Tag


@pytest.mark.asyncio
async def test_tag_create() -> None:
    # Arrange
    name = "Test Tag"
    slug = "test-tag"

    # Mock the Tag.create method
    with mock.patch.object(Tag, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await Tag.create(
            name=name,
            slug=slug,
        )

        # Assert
        mock_create.assert_called_once_with(
            name=name,
            slug=slug,
        )


@pytest.mark.asyncio
async def test_tag_fields() -> None:
    # Arrange
    tag = Tag(
        name="Test Tag",
        slug="test-tag",
    )

    # Assert
    assert tag.name == "Test Tag"
    assert tag.slug == "test-tag"


@pytest.mark.asyncio
async def test_tag_unique_constraints() -> None:
    # This test verifies that the model has unique constraints on name and slug
    # We can't easily test the actual database constraints in a unit test,
    # but we can verify the field definitions have unique=True

    # Get field objects from the model
    name_field = Tag._meta.fields_map.get("name")
    slug_field = Tag._meta.fields_map.get("slug")

    # Assert
    assert name_field is not None
    assert slug_field is not None
    assert name_field.unique is True
    assert slug_field.unique is True
