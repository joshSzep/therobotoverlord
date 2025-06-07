# Standard library imports
from slugify import slugify

# Project-specific imports
from backend.converters import tag_to_schema
from backend.db.models.tag import Tag
from backend.db_functions.tags.get_tag_by_name import get_tag_by_name
from backend.schemas.tag import TagResponse


async def get_or_create_tag_by_name(name: str) -> TagResponse:
    # First try to get the tag by name
    tag = await get_tag_by_name(name)

    # If tag doesn't exist, create it
    if not tag:
        # Create a slug from the name
        slug = slugify(name)

        # Create the tag
        tag_model = await Tag.create(name=name, slug=slug)
        tag = await tag_to_schema(tag_model)

    return tag
