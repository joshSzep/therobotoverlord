from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from backend.db.models.user import User
from backend.db_functions.pending_posts.list_pending_posts import (
    list_pending_posts as db_list_pending_posts,
)
from backend.schemas.pending_post import PendingPostList
from backend.utils.auth import get_current_user
from backend.utils.role_check import check_is_admin

# Create a router for this endpoint
router = APIRouter()


@router.get("/", response_model=PendingPostList)
async def list_pending_posts(
    current_user: User = Depends(get_current_user),
    topic_id: Optional[UUID] = Query(None, description="Filter by topic ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PendingPostList:
    """
    List all pending posts awaiting moderation.
    Only accessible to administrators.
    """
    # Check if user is admin
    is_user_admin = await check_is_admin(current_user.id)
    if not is_user_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this endpoint",
        )

    return await db_list_pending_posts(
        topic_id=topic_id,
        limit=limit,
        offset=offset,
    )
