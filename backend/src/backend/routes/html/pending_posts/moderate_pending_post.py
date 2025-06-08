from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import RedirectResponse

from backend.db_functions.pending_posts.approve_and_create_post import (
    approve_and_create_post,
)
from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.db_functions.pending_posts.reject_pending_post import reject_pending_post
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user
from backend.utils.role_check import check_is_admin

# Create router for this endpoint
router = APIRouter()

# Export the router
__all__ = ["router"]


@router.post("/{pending_post_id}/moderate/")
async def moderate_pending_post_html(
    request: Request,
    pending_post_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    action: str = Form(...),
    moderation_reason: str = Form(None),
) -> RedirectResponse:
    """
    HTML endpoint for moderating a pending post.

    Only administrators can moderate pending posts.
    Regular users cannot moderate any posts, including their own.
    """
    # Get the pending post
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

    # Perform the moderation action
    if action.lower() == "approve":
        await approve_and_create_post(pending_post_id=pending_post_id)
        return RedirectResponse(
            url=f"/html/posts/{pending_post_id}/",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    elif action.lower() == "reject":
        await reject_pending_post(
            pending_post_id=pending_post_id,
            moderation_reason=moderation_reason or "Rejected by moderator",
        )
        return RedirectResponse(
            url="/html/pending-posts/",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Action must be either "approve" or "reject"',
        )
