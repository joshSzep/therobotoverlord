# Standard library imports

# Project-specific imports
from backend.converters import tag_to_schema
from backend.db.models.tag import Tag
from backend.schemas.tag import TagResponse


async def create_tag(name: str, slug: str) -> TagResponse:
    tag = await Tag.create(name=name, slug=slug)
    return await tag_to_schema(tag)
