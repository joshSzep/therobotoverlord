# Standard library imports
from typing import Optional

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.db_functions.tags import list_tags as db_list_tags
from backend.schemas.tag import TagList

router = APIRouter()


@router.get("/", response_model=TagList)
async def list_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
) -> TagList:
    # Use the data access function to fetch tags and return the TagList directly
    # The function handles the conversion from ORM models to schema objects
    return await db_list_tags(skip, limit, search)
