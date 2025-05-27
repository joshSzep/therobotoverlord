# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import tag_to_schema
from backend.db.models.tag import Tag
from backend.schemas.tag import TagResponse


async def update_tag(tag_id: UUID, name: str, slug: str) -> Optional[TagResponse]:
    tag = await Tag.get_or_none(id=tag_id)
    if tag:
        tag.name = name
        tag.slug = slug
        await tag.save()
        return await tag_to_schema(tag)
    return None
