# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.db.models.tag import Tag


async def delete_tag(tag_id: UUID) -> bool:
    tag = await Tag.get_or_none(id=tag_id)
    if tag:
        await tag.delete()
        return True
    return False
