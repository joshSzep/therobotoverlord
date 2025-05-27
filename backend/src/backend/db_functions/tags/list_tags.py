# Standard library imports
from typing import Optional

# Project-specific imports
from backend.converters import tag_to_schema
from backend.db.models.tag import Tag
from backend.schemas.tag import TagList
from backend.schemas.tag import TagResponse


async def list_tags(
    skip: int = 0, limit: int = 50, search: Optional[str] = None
) -> TagList:
    query = Tag.all()

    if search:
        query = query.filter(name__icontains=search)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    tags = await query.offset(skip).limit(limit)

    # Convert ORM models to schema objects using async converter
    tag_responses: list[TagResponse] = []
    for tag in tags:
        tag_responses.append(await tag_to_schema(tag))

    return TagList(tags=tag_responses, count=count)
