# Standard library imports
from typing import Annotated
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import status
from fastapi.responses import RedirectResponse
from starlette.responses import RedirectResponse as StarletteRedirectResponse

# Project-specific imports
from backend.db_functions.posts.create_post import create_post
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_class=RedirectResponse)
async def create_post_action(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    content: str = Form(...),
    topic_id: UUID = Form(...),
) -> StarletteRedirectResponse:
    # Create post
    await create_post(content=content, author_id=current_user.id, topic_id=topic_id)

    # Redirect to the topic detail page
    return StarletteRedirectResponse(
        url=f"/html/topics/{topic_id}/",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{post_id}/reply/", response_class=RedirectResponse)
async def create_reply_action(
    post_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    content: str = Form(...),
) -> StarletteRedirectResponse:
    # Create reply
    await create_post(
        content=content,
        author_id=current_user.id,
        # Placeholder, will be updated from parent
        topic_id=UUID("00000000-0000-0000-0000-000000000000"),
        parent_post_id=post_id,
    )

    # Redirect to the parent post detail page
    return StarletteRedirectResponse(
        url=f"/html/posts/{post_id}/",
        status_code=status.HTTP_303_SEE_OTHER,
    )
