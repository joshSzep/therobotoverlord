# Standard library imports
from typing import Optional

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.converters import tag_to_schema
from backend.repositories.tag_repository import TagRepository
from backend.schemas.tag import TagList
from backend.schemas.tag import TagResponse

router = APIRouter()


@router.get("/", response_model=TagList)
async def list_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
) -> TagList:
    # Use the repository to fetch tags
    tags, count = await TagRepository.list_tags(skip, limit, search)

    # Convert to response model using our converter
    tag_responses: list[TagResponse] = []
    for tag in tags:
        tag_responses.append(await tag_to_schema(tag))

    return TagList(tags=tag_responses, count=count)
