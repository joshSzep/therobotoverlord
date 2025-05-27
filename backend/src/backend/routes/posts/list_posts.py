# Standard library imports
from typing import Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.db_functions.posts import list_posts as db_list_posts
from backend.schemas.post import PostList

router = APIRouter()


@router.get("/", response_model=PostList)
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    topic_id: Optional[UUID] = None,
    author_id: Optional[UUID] = None,
) -> PostList:
    return await db_list_posts(
        skip=skip, limit=limit, topic_id=topic_id, author_id=author_id
    )
