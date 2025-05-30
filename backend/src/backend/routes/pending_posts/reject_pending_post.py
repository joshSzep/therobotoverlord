from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import status

from backend.db.models.user import User
from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.db_functions.pending_posts.reject_pending_post import reject_pending_post
from backend.schemas.rejected_post import RejectedPostResponse
from backend.schemas.rejected_post import RejectionRequest
from backend.utils.role_check import get_admin_user

router = APIRouter()


@router.post("/{pending_post_id}/reject/", response_model=RejectedPostResponse)
async def reject_pending_post_route(
    rejection_data: RejectionRequest,
    pending_post_id: UUID = Path(
        ..., description="The ID of the pending post to reject"
    ),
    current_user: User = Depends(get_admin_user),
) -> RejectedPostResponse:
    """
    Reject a pending post and create a rejected post entry.
    Only accessible to administrators.
    """
    # First check if the pending post exists
    pending_post = await get_pending_post_by_id(pending_post_id)
    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending post not found",
        )

    # Reject the pending post
    rejected_post = await reject_pending_post(
        pending_post_id=pending_post_id,
        moderation_reason=rejection_data.reason,
    )

    if not rejected_post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject pending post",
        )

    return rejected_post
