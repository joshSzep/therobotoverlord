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
from backend.db_functions.pending_posts.create_pending_post import create_pending_post
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user
from backend.schemas.pending_post import PendingPostCreate
from backend.tasks.ai_moderation_task import schedule_post_moderation

router = APIRouter()


@router.post("/", response_class=RedirectResponse)
async def create_post_action(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    content: str = Form(...),
    topic_id: UUID = Form(...),
) -> StarletteRedirectResponse:
    # Create pending post
    pending_post_data = PendingPostCreate(
        content=content,
        topic_id=topic_id,
    )

    new_pending_post = await create_pending_post(
        user_id=current_user.id,
        pending_post_data=pending_post_data,
    )

    # Schedule the post for moderation
    await schedule_post_moderation(new_pending_post.id)

    # Redirect to the topic detail page with a message
    message = "Your post has been submitted for moderation"
    redirect_url = f"/html/topics/{topic_id}/?message={message}"
    return StarletteRedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{post_id}/reply/", response_class=RedirectResponse)
async def create_reply_action(
    post_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    content: str = Form(...),
    topic_id: UUID = Form(...),
) -> StarletteRedirectResponse:
    # Create pending reply
    pending_post_data = PendingPostCreate(
        content=content,
        topic_id=topic_id,
        parent_post_id=post_id,
    )

    new_pending_post = await create_pending_post(
        user_id=current_user.id,
        pending_post_data=pending_post_data,
    )

    # Schedule the post for moderation
    await schedule_post_moderation(new_pending_post.id)

    # Redirect to the topic page with a message
    message = "Your reply has been submitted for moderation"
    redirect_url = f"/html/topics/{topic_id}/?message={message}"
    return StarletteRedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_303_SEE_OTHER,
    )
