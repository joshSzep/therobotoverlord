# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import tag_to_schema
from backend.db.models.tag import Tag
from backend.schemas.tag import TagResponse


async def get_tag_by_id(tag_id: UUID) -> Optional[TagResponse]:
    tag = await Tag.get_or_none(id=tag_id)
    if tag:
        return await tag_to_schema(tag)
    return None
