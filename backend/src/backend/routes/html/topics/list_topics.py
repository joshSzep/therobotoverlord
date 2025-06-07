# Standard library imports
from typing import Annotated
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import Query
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from starlette.responses import RedirectResponse as StarletteRedirectResponse

# Project-specific imports
from backend.db_functions.tags.get_or_create_tag_by_name import (
    get_or_create_tag_by_name,
)
from backend.db_functions.topic_tags import add_tags_to_topic
from backend.db_functions.topics import create_topic
from backend.db_functions.topics import list_topics
from backend.dominate_templates.topics.list import create_topics_list_page
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user
from backend.routes.html.utils.auth import get_current_user_optional

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def list_topics_page(
    request: Request,
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> HTMLResponse:
    # Get topics with pagination
    skip = (page - 1) * limit
    topics_data = await list_topics(skip=skip, limit=limit)

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
        topics=topics,  # Pass schema objects directly
        pagination=pagination,
        user=current_user,  # Pass schema object directly
        messages=[],  # Empty list instead of None
    )

    # Return the rendered HTML
    return HTMLResponse(str(doc))


@router.post("/", response_class=RedirectResponse)
async def create_topic_action(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form(None),
) -> StarletteRedirectResponse:
    # Create topic
    topic = await create_topic(
        title=title,
        description=description,  # Use the description from the form
        created_by_id=current_user.id,
    )

    # Process tags if provided
    if tags:
        tag_names = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_names:
            # Get or create tags and collect their IDs
            tag_ids: list[UUID] = []
            for tag_name in tag_names:
                tag = await get_or_create_tag_by_name(tag_name)
                tag_ids.append(tag.id)

            # Add tags to the topic
            await add_tags_to_topic(topic_id=topic.id, tag_ids=tag_ids)

    # Redirect to the topic detail page
    return StarletteRedirectResponse(
        url=f"/html/topics/{topic.id}/",
        status_code=status.HTTP_303_SEE_OTHER,
    )
