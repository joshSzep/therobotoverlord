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
from backend.dominate_templates import create_home_page
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional

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

    # Create the home page using Dominate
    doc = create_home_page(
        topics=topics,  # Pass schema objects directly
        posts=posts,  # Pass schema objects directly
        user=current_user,  # Pass schema object directly
    )

    # Convert the document to HTML and return as an HTMLResponse
    html_content = str(doc)
    return HTMLResponse(content=html_content)
