# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Request
from fastapi.responses import HTMLResponse

# Project-specific imports
from backend.db_functions.tags.get_tag_by_slug import get_tag_by_slug
from backend.db_functions.topics.list_topics_by_tag_slug import list_topics_by_tag_slug
from backend.dominate_templates.topics.list import create_topics_list_page
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional

router = APIRouter()


@router.get("/{tag_slug}/", response_class=HTMLResponse)
async def list_topics_by_tag_page(
    request: Request,
    tag_slug: str,
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> HTMLResponse:
    # Get topics with pagination filtered by tag
    skip = (page - 1) * limit
    topics_data = await list_topics_by_tag_slug(
        tag_slug=tag_slug,
        skip=skip,
        limit=limit,
    )

    # Get tag for display
    tag = await get_tag_by_slug(tag_slug)
    tag_name = tag.name if tag else tag_slug

    # Extract topics and total count
    topics = topics_data.topics
    total_count = topics_data.count
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

    # Create the topics list page using Dominate
    doc = create_topics_list_page(
        topics=topics,
        pagination=pagination,
        user=current_user,
        messages=[],
        tag_filter=tag_name,  # Pass the tag name for display
    )

    # Return the rendered HTML
    return HTMLResponse(str(doc))
