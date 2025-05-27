# Standard library imports
from typing import Optional

# Project-specific imports
from backend.converters import tag_to_schema
from backend.db.models.tag import Tag
from backend.schemas.tag import TagResponse


async def get_tag_by_slug(slug: str) -> Optional[TagResponse]:
    tag = await Tag.get_or_none(slug=slug)
    if tag:
        return await tag_to_schema(tag)
    return None
