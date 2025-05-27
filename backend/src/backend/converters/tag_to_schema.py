from backend.db.models.tag import Tag
from backend.schemas.tag import TagResponse


async def tag_to_schema(tag: Tag) -> TagResponse:
    return TagResponse(
        id=tag.id,
        name=tag.name,
        slug=tag.slug,
    )
