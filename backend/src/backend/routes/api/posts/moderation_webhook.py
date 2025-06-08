# Standard library imports
from typing import Any
from typing import Dict
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel

# Project-specific imports
from backend.db.models.pending_post import PendingPost
from backend.db_functions.pending_posts.approve_and_create_post import (
    approve_and_create_post,
)
from backend.db_functions.pending_posts.reject_pending_post import reject_pending_post
from backend.db_functions.user_events.create_event import create_event
from backend.utils.api_auth import verify_api_key
from backend.utils.rate_limiter import limit_moderation_requests

router = APIRouter()


class ModerationResult(BaseModel):
    pending_post_id: UUID
    status: str  # "approved" or "rejected"
    feedback: str = ""
    confidence: float = 0.0


def log_moderation_event(
    background_tasks: BackgroundTasks,
    user_id: UUID,
    event_type: str,
    pending_post_id: str,
    topic_id: str,
    confidence: float,
    feedback: str = "",
) -> None:
    """Helper function to create moderation event in background task"""
    metadata = {
        "pending_post_id": pending_post_id,
        "topic_id": topic_id,
        "confidence": confidence,
    }

    if feedback and feedback.strip():
        metadata["feedback"] = feedback

    background_tasks.add_task(
        create_event,
        user_id=user_id,
        event_type=event_type,
        resource_type="post",
        metadata=metadata,
    )


@router.post("/", status_code=status.HTTP_200_OK)
async def moderation_webhook(
    background_tasks: BackgroundTasks,
    moderation_result: ModerationResult,
    api_key: str = Depends(verify_api_key),
    _: None = Depends(limit_moderation_requests),
) -> Dict[str, Any]:
    # Get the pending post directly from the model, not the schema
    pending_post = await PendingPost.get_or_none(id=moderation_result.pending_post_id)

    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending post not found",
        )

    # Get related objects
    await pending_post.fetch_related("author", "topic")
    author = pending_post.author
    topic = pending_post.topic

    # Process the moderation result
    if moderation_result.status.lower() == "approved":
        # Approve the post
        await approve_and_create_post(pending_post_id=pending_post.id)

        # Log approval event
        log_moderation_event(
            background_tasks=background_tasks,
            user_id=author.id,
            event_type="post_approved",
            pending_post_id=str(pending_post.id),
            topic_id=str(topic.id),
            confidence=moderation_result.confidence,
        )
    else:  # rejected
        # Reject the post
        await reject_pending_post(
            pending_post_id=pending_post.id,
            moderation_reason=moderation_result.feedback,
        )

        # Log rejection event
        log_moderation_event(
            background_tasks=background_tasks,
            user_id=author.id,
            event_type="post_rejected",
            pending_post_id=str(pending_post.id),
            topic_id=str(topic.id),
            confidence=moderation_result.confidence,
            feedback=moderation_result.feedback,
        )

    return {
        "status": "success",
        "message": f"Post moderation processed: {moderation_result.status}",
    }
