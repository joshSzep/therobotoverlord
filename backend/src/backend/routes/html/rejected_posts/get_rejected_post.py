from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse

from backend.db_functions.rejected_posts.get_rejected_post_by_id import (
    get_rejected_post_by_id,
)
from backend.dominate_templates.rejected_posts.detail import (
    create_rejected_post_detail_page,
)
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user
from backend.utils.role_check import check_is_admin

# Create router for this endpoint
router = APIRouter()

# Export the router
__all__ = ["router"]


@router.get("/{rejected_post_id}/", response_class=HTMLResponse)
async def get_rejected_post_html(
    request: Request,
    rejected_post_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> HTMLResponse:
    """
    HTML page for viewing a single rejected post.

    Shows the rejected post details and allows for resubmission or deletion.
    """
    # Check if user is an admin
    is_user_admin = await check_is_admin(current_user.id)

    # Get the rejected post
    rejected_post = await get_rejected_post_by_id(rejected_post_id)

    if not rejected_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rejected post not found",
        )

    # Check if user is authorized to view this post
    is_owner = rejected_post.author.id == current_user.id

    if not (is_owner or is_user_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this rejected post",
        )

    html_content = create_rejected_post_detail_page(
        rejected_post=rejected_post,
        is_admin=is_user_admin,
        current_user=current_user,
    )

    return HTMLResponse(content=html_content)
