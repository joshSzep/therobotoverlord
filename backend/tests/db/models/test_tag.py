import pytest
from slugify import slugify

from backend.db.models.tag import Tag


@pytest.mark.asyncio
async def test_tag_create() -> None:
    # Arrange
    tag_name = "Test Tag"

    # Act
    tag = Tag(name=tag_name, slug=slugify(tag_name))
    await tag.save()

    # Assert
    assert tag.id is not None
    assert tag.name == tag_name
    assert tag.slug == slugify(tag_name)
    assert tag.created_at is not None
    assert tag.updated_at is not None


@pytest.mark.asyncio
async def test_tag_create_with_special_chars() -> None:
    # Arrange
    tag_name = "Test & Special Chars!"

    # Act
    tag = Tag(name=tag_name, slug=slugify(tag_name))
    await tag.save()

    # Assert
    assert tag.name == tag_name
    assert tag.slug == slugify(tag_name)


@pytest.mark.asyncio
async def test_tag_unique_name_constraint() -> None:
    # Arrange
    tag_name = "Unique Tag"
    tag1 = Tag(name=tag_name, slug=slugify(tag_name))
    await tag1.save()

    # Act & Assert
    tag2 = Tag(name=tag_name, slug=slugify(tag_name))
    with pytest.raises(Exception):
        await tag2.save()


@pytest.mark.asyncio
async def test_tag_update() -> None:
    # Arrange
    tag = Tag(name="Original Tag", slug=slugify("Original Tag"))
    await tag.save()
    original_created_at = tag.created_at
    original_slug = tag.slug

    # Act
    tag.name = "Updated Tag"
    tag.slug = slugify("Updated Tag")
    await tag.save()

    # Assert
    assert tag.name == "Updated Tag"
    assert tag.slug == slugify("Updated Tag")
    assert tag.slug != original_slug
    assert tag.created_at == original_created_at
    assert tag.updated_at > original_created_at


@pytest.mark.asyncio
async def test_tag_delete() -> None:
    # Arrange
    tag = Tag(name="Tag to Delete", slug=slugify("Tag to Delete"))
    await tag.save()
    tag_id = tag.id

    # Act
    await tag.delete()

    # Assert
    retrieved_tag = await Tag.get_or_none(id=tag_id)
    assert retrieved_tag is None
