from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse

from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.dominate_templates.pending_posts.detail import (
    create_pending_post_detail_page,
)
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user
from backend.utils.role_check import check_is_admin

# Create router for this endpoint
router = APIRouter()

# Export the router
__all__ = ["router"]


@router.get("/{pending_post_id}/", response_class=HTMLResponse)
async def get_pending_post_html(
    request: Request,
    pending_post_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> HTMLResponse:
    """
    HTML page for viewing a single pending post.

    Shows the pending post details and moderation controls for admins.
    Regular users can only view their own pending posts.
    """
    # Get the pending post
    pending_post = await get_pending_post_by_id(pending_post_id)

    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pending post with ID {pending_post_id} not found",
        )

    # Check if user is authorized to view this post
    is_user_admin = await check_is_admin(current_user.id)
    is_owner = pending_post.author.id == current_user.id

    if not (is_owner or is_user_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this post",
        )

    # Create the pending post detail page using Dominate
    doc = create_pending_post_detail_page(
        pending_post=pending_post,
        user=current_user,
        is_admin=is_user_admin,
        is_owner=is_owner,
        messages=[],
    )

    # Return the rendered HTML
    return HTMLResponse(str(doc))
