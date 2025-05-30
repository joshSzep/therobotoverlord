from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import status

from backend.db.models.user import User
from backend.db_functions.pending_posts.approve_and_create_post import (
    approve_and_create_post,
)
from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.schemas.post import PostResponse
from backend.utils.role_check import get_admin_user

router = APIRouter()


@router.post("/{pending_post_id}/approve/", response_model=PostResponse)
async def approve_pending_post(
    pending_post_id: UUID = Path(
        ..., description="The ID of the pending post to approve"
    ),
    current_user: User = Depends(get_admin_user),
) -> PostResponse:
    """
    Approve a pending post and create a regular post from it.
    Only accessible to administrators.
    """
    # First check if the pending post exists
    pending_post = await get_pending_post_by_id(pending_post_id)
    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending post not found",
        )

    # Approve the pending post
    approved_post = await approve_and_create_post(pending_post_id)
    if not approved_post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve pending post",
        )

    return approved_post
