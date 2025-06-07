# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

# Project-specific imports
from backend.db_functions.posts import list_posts
from backend.db_functions.topics import list_topics
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional
from backend.utils.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
) -> HTMLResponse:
    # Get featured topics
    topics_data = await list_topics(skip=0, limit=5)
    topics = topics_data.topics

    # Get recent posts
    posts_data = await list_posts(skip=0, limit=10)
    posts = posts_data.posts

    return templates.TemplateResponse(
        "pages/home.html",
        {
            "request": request,
            "user": current_user,
            "topics": topics,
            "posts": posts,
        },
    )
