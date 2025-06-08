# Standard library imports
from typing import Any

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import Response

# Project-specific imports
from backend.db_functions.pending_posts.list_pending_posts import list_pending_posts
from backend.utils.role_check import get_admin_user

router = APIRouter()


@router.get("/")
async def moderation_dashboard(
    request: Request,
    _: Any = Depends(get_admin_user),
) -> Response:
    """
    Admin moderation dashboard for reviewing pending posts.
    """
    # Get pending posts
    pending_posts = await list_pending_posts(limit=20)

    # Get counts for dashboard stats
    pending_count = pending_posts.count

    # Return the dashboard template
    context = {
        "request": request,
        "pending_count": pending_count,
        "pending_posts": pending_posts.pending_posts,
        "title": "Moderation Dashboard",
    }

    # This would normally use a template, but for now just return JSON
    return Response(
        content=str(context),
        media_type="text/plain",
    )
