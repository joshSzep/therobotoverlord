from typing import Annotated
from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Request
from fastapi.responses import HTMLResponse

from backend.db_functions.pending_posts.list_pending_posts import list_pending_posts
from backend.dominate_templates.pending_posts.list import create_pending_posts_list_page
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user
from backend.utils.role_check import check_is_admin

# Create router for this endpoint
router = APIRouter()

# Export the router
__all__ = ["router"]


@router.get("/", response_class=HTMLResponse)
async def list_pending_posts_html(
    request: Request,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    topic_id: Optional[UUID] = Query(None, description="Filter by topic ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> HTMLResponse:
    """
    HTML page for viewing pending posts.

    Shows all pending posts for admins, but only the user's own pending posts
    for regular users. Admin users will see moderation controls.
    """
    # Check if user is an admin
    is_user_admin = await check_is_admin(current_user.id)

    # Calculate offset from page number
    offset = (page - 1) * limit

    # For regular users, only show their own pending posts
    user_id = None if is_user_admin else current_user.id

    pending_posts_data = await list_pending_posts(
        user_id=user_id,
        topic_id=topic_id,
        limit=limit,
        offset=offset,
    )

    # Extract pending posts and total count
    pending_posts = pending_posts_data.pending_posts
    total_count = pending_posts_data.count
    total_pages = (total_count + limit - 1) // limit

    # Create pagination data
    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
        "previous_page": page - 1,
        "next_page": page + 1,
    }

    # Create the pending posts list page using Dominate
    doc = create_pending_posts_list_page(
        pending_posts=pending_posts,
        pagination=pagination,
        user=current_user,
        is_admin=is_user_admin,
        messages=[],
    )

    # Return the rendered HTML
    return HTMLResponse(str(doc))
