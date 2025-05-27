# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

# Project-specific imports
from backend.db_functions.posts import get_post_by_id
from backend.db_functions.posts import list_post_replies as db_list_post_replies
from backend.schemas.post import PostList

router = APIRouter()


@router.get("/{post_id}/replies/", response_model=PostList)
async def list_post_replies(
    post_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PostList:
    # Verify that the parent post exists
    parent_post = await get_post_by_id(post_id)
    if not parent_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent post not found",
        )

    # Get replies to the post using data access function
    return await db_list_post_replies(post_id, skip, limit)
