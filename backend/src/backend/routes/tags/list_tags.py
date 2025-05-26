# Standard library imports
from typing import Optional

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.db.models.tag import Tag
from backend.routes.tags.schemas import TagList
from backend.routes.tags.schemas import TagResponse

router = APIRouter()


@router.get("/", response_model=TagList)
async def list_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
) -> TagList:
    query = Tag.all()

    if search:
        # Filter by name if search parameter is provided
        query = query.filter(name__icontains=search)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    tags = await query.offset(skip).limit(limit)

    # Convert to response model
    tag_responses = [TagResponse.model_validate(tag) for tag in tags]

    return TagList(tags=tag_responses, count=count)
