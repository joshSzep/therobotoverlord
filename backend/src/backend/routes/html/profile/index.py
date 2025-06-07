# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.db_functions.posts.list_pending_posts_by_user import (
    list_pending_posts_by_user,
)

# Project-specific imports
from backend.db_functions.posts.list_posts_by_user import list_posts_by_user
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user
from backend.routes.html.utils.template_config import render_template

router = APIRouter()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="src/backend/templates")


@router.get("/", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    post_page: int = Query(1, ge=1),
    post_limit: int = Query(5, ge=1, le=20),
) -> HTMLResponse:
    # Get user's posts with pagination
    post_offset = (post_page - 1) * post_limit
    user_posts = await list_posts_by_user(
        current_user.id, limit=post_limit, offset=post_offset
    )

    # Get total count for pagination
    total_post_count = await list_posts_by_user(current_user.id, count_only=True)
    # Use ternary operator to handle type checking
    post_count = total_post_count if isinstance(total_post_count, int) else 0
    total_post_pages = (post_count + post_limit - 1) // post_limit

    # Create pagination data for posts
    post_pagination = {
        "current_page": post_page,
        "total_pages": total_post_pages,
        "has_previous": post_page > 1,
        "has_next": post_page < total_post_pages,
        "previous_page": post_page - 1,
        "next_page": post_page + 1,
    }

    # Get user's pending posts
    pending_posts = await list_pending_posts_by_user(current_user.id, limit=5)

    return render_template(
        request,
        "pages/profile/index.html",
        {
            "user": current_user,
            "user_posts": user_posts,
            "post_pagination": post_pagination,
            "pending_posts": pending_posts,
        },
    )
