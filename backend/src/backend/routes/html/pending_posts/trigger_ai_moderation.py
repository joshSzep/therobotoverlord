from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import RedirectResponse

from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user
from backend.tasks.ai_moderation_task import process_pending_post
from backend.utils.role_check import check_is_admin

# Create router for this endpoint
router = APIRouter()

# Export the router
__all__ = ["router"]


@router.post("/{pending_post_id}/trigger-ai-moderation/")
async def trigger_ai_moderation_html(
    request: Request,
    pending_post_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> RedirectResponse:
    """
    HTML endpoint for triggering AI moderation for a pending post.

    Only administrators can trigger AI moderation for pending posts.
    """
    # Get the pending post
    pending_post = await get_pending_post_by_id(pending_post_id)

    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pending post with ID {pending_post_id} not found",
        )

    # Only admins can trigger AI moderation
    is_user_admin = await check_is_admin(current_user.id)

    if not is_user_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can trigger AI moderation",
        )

    # Process the pending post through the AI moderation pipeline
    try:
        await process_pending_post(pending_post_id)
    except Exception as e:
        # Log the error
        import logging

        logging.error(f"Error triggering AI moderation: {str(e)}")
        # Redirect back to the pending post with an error message
        return RedirectResponse(
            url=f"/html/pending-posts/{pending_post_id}/?error=ai_moderation_failed",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Redirect back to the pending post
    return RedirectResponse(
        url=f"/html/pending-posts/{pending_post_id}/?success=ai_moderation_triggered",
        status_code=status.HTTP_303_SEE_OTHER,
    )
