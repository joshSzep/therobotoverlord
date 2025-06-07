# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Request
from fastapi.responses import HTMLResponse

# Project-specific imports
from backend.db_functions.posts import list_posts
from backend.db_functions.posts.enhance_posts_with_topics import (
    enhance_posts_with_topics,
)
from backend.dominate_templates.posts.list import create_posts_list_page
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def list_posts_page(
    request: Request,
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> HTMLResponse:
    # Calculate skip value for pagination
    skip = (page - 1) * limit

    # Get posts with pagination
    posts_data = await list_posts(skip=skip, limit=limit)

    # Extract posts and total count
    posts = posts_data.posts
    total_count = posts_data.count
    total_pages = (total_count + limit - 1) // limit

    # Fetch topic information for all posts
    topic_map = await enhance_posts_with_topics(posts)

    # Create pagination data
    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
        "previous_page": page - 1,
        "next_page": page + 1,
    }

    # Create the posts list page using Dominate
    doc = create_posts_list_page(
        posts=posts,
        pagination=pagination,
        user=current_user,
        topic_map=topic_map,
    )

    # Return the rendered HTML
    return HTMLResponse(str(doc))
