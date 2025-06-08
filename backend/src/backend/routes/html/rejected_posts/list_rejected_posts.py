from typing import Annotated
from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi.responses import HTMLResponse
from starlette.requests import Request

from backend.db_functions.rejected_posts.list_rejected_posts import list_rejected_posts
from backend.dominate_templates.rejected_posts.list import (
    create_rejected_posts_list_page,
)
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user
from backend.utils.role_check import is_admin

# Create router for this endpoint
router = APIRouter()

# Export the router
__all__ = ["router"]


@router.get("/", response_class=HTMLResponse)
async def list_rejected_posts_html(
    request: Request,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    topic_id: Optional[UUID] = Query(None, description="Filter by topic ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> HTMLResponse:
    """
    HTML page for viewing rejected posts.

    If user is admin, shows all rejected posts.
    Otherwise, only shows the rejected posts of the logged-in user.
    """
    # Check if user is admin
    user_is_admin = is_admin(current_user.role)

    # If not admin, only show user's own rejected posts
    user_id = None if user_is_admin else current_user.id

    # Get rejected posts
    rejected_posts_list = await list_rejected_posts(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )

    # Create HTML page
    html_content = create_rejected_posts_list_page(
        rejected_posts=rejected_posts_list.rejected_posts,
        count=rejected_posts_list.count,
        limit=limit,
        offset=offset,
        is_admin=user_is_admin,
        current_user=current_user,
    )

    return HTMLResponse(content=html_content)
