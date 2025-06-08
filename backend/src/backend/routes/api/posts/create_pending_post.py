# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from tortoise.exceptions import ValidationError

# Project-specific imports
from backend.db.models.user import User
from backend.db_functions.pending_posts.create_pending_post import (
    create_pending_post as db_create_pending_post,
)
from backend.db_functions.posts.get_post_by_id import get_post_by_id
from backend.db_functions.topics.get_topic_by_id import get_topic_by_id
from backend.schemas.pending_post import PendingPostCreate
from backend.schemas.pending_post import PendingPostResponse
from backend.tasks.ai_moderation_task import schedule_post_moderation
from backend.utils.auth import get_current_user

router = APIRouter()


@router.post(
    "/", response_model=PendingPostResponse, status_code=status.HTTP_201_CREATED
)
async def create_pending_post(
    post_data: PendingPostCreate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> PendingPostResponse:
    # Verify that the topic exists
    topic = await get_topic_by_id(post_data.topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Verify that the parent post exists and belongs to the same topic if provided
    if post_data.parent_post_id:
        parent_post = await get_post_by_id(post_data.parent_post_id)
        if not parent_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent post not found",
            )

        # Check if parent post belongs to the same topic
        if str(parent_post.topic_id) != str(post_data.topic_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent post must belong to the same topic",
            )

    try:
        # Create the pending post
        pending_post = await db_create_pending_post(
            user_id=current_user.id,
            pending_post_data=post_data,
        )

        # Schedule moderation task for the pending post
        await schedule_post_moderation(pending_post_id=pending_post.id)

        return pending_post
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
