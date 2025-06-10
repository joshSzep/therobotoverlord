from uuid import UUID

from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from backend.db.models.user import User
from backend.db_functions.pending_posts.approve_and_create_post import (
    approve_and_create_post,
)
from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.db_functions.pending_posts.reject_pending_post import reject_pending_post
from backend.routes.pending_posts import router
from backend.schemas.pending_post import PendingPostResponse
from backend.utils.auth import get_current_user
from backend.utils.role_check import check_is_admin


@router.post("/{pending_post_id}/moderate/", status_code=status.HTTP_200_OK)
async def moderate_pending_post(
    pending_post_id: UUID,
    action: str = Body(..., embed=True),
    reason: str = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
) -> PendingPostResponse:
    """
    Moderate a pending post by approving or rejecting it.

    Only accessible by admin users.

    Args:
        pending_post_id: ID of the pending post to moderate
        action: Either "approve" or "reject"
        reason: Optional reason for rejection
        current_user: Current user

    Returns:
        PendingPostResponse: The moderated post
    """
    pending_post = await get_pending_post_by_id(pending_post_id)

    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pending post with ID {pending_post_id} not found",
        )

    # Only admins can moderate posts
    is_user_admin = await check_is_admin(current_user.id)

    if not is_user_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can moderate posts",
        )

    if action.lower() == "approve":
        await approve_and_create_post(pending_post_id=pending_post_id)
        return pending_post
    elif action.lower() == "reject":
        if not reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A reason must be provided when rejecting a post",
            )
        await reject_pending_post(
            pending_post_id=pending_post_id,
            moderation_reason=reason,
        )
        return pending_post
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Action must be either "approve" or "reject"',
        )
