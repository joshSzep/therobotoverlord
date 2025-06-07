# Standard library imports
import logging
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

# Project-specific imports
from backend.db_functions.posts import list_posts_by_topic
from backend.db_functions.topics import get_topic_by_id
from backend.dominate_templates.topics.detail import create_topic_detail_page
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{topic_id}/", response_class=HTMLResponse)
async def get_topic_page(
    request: Request,
    topic_id: UUID,
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> HTMLResponse:
    # Get topic
    topic = await get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Get posts for this topic with pagination
    skip = (page - 1) * limit
    posts_data = await list_posts_by_topic(topic_id, skip=skip, limit=limit)

    # Extract posts and total count
    posts = posts_data.posts
    total_count = posts_data.count
    total_pages = (total_count + limit - 1) // limit

    # Debug logging for posts
    logger.debug(f"Retrieved {len(posts)} posts for topic {topic_id}")

    # Create pagination data
    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
        "previous_page": page - 1,
        "next_page": page + 1,
    }

    # Create the topic detail page using Dominate
    doc = create_topic_detail_page(
        topic=topic,  # Pass schema object directly
        posts=posts,  # Pass schema objects directly
        pagination=pagination,
        user=current_user,  # Pass schema object directly
    )

    # Return the rendered HTML
    return HTMLResponse(str(doc))
