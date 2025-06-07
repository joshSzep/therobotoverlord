# Standard library imports
from typing import Annotated
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Project-specific imports
from backend.db_functions.posts import get_post_by_id
from backend.db_functions.posts import list_post_replies
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional

router = APIRouter()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="src/backend/templates")


@router.get("/{post_id}/", response_class=HTMLResponse)
async def get_post_page(
    request: Request,
    post_id: UUID,
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> HTMLResponse:
    # Get post
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Get replies for this post with pagination
    skip = (page - 1) * limit
    replies_data = await list_post_replies(post_id, skip=skip, limit=limit)

    # Extract replies and total count
    replies = replies_data.posts
    total_count = replies_data.count
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

    return templates.TemplateResponse(
        "pages/posts/detail.html",
        {
            "request": request,
            "user": current_user,
            "post": post,
            "replies": replies,
            "pagination": pagination,
        },
    )
