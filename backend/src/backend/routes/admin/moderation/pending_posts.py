# Standard library imports
from typing import Any
from typing import Dict
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

# Project-specific imports
from backend.db_functions.pending_posts.approve_and_create_post import (
    approve_and_create_post,
)
from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.db_functions.pending_posts.list_pending_posts import list_pending_posts
from backend.db_functions.pending_posts.reject_pending_post import reject_pending_post
from backend.db_functions.user_events.create_event import create_event
from backend.schemas.pending_post import PendingPostList
from backend.utils.role_check import get_admin_user

router = APIRouter()


@router.get("/", response_model=PendingPostList)
async def list_all_pending_posts(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _: Any = Depends(get_admin_user),
) -> PendingPostList:
    """
    List all pending posts for admin moderation.
    """
    return await list_pending_posts(limit=limit, offset=offset)


@router.post("/{pending_post_id}/approve/")
async def approve_pending_post(
    pending_post_id: UUID,
    background_tasks: BackgroundTasks,
    _: Any = Depends(get_admin_user),
) -> Dict[str, Any]:
    """
    Approve a pending post and create a regular post.
    """
    # Get the pending post
    pending_post = await get_pending_post_by_id(pending_post_id)
    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending post not found",
        )

    # Approve the post
    post = await approve_and_create_post(pending_post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve post",
        )

    # Log the event
    background_tasks.add_task(
        create_event,
        user_id=post.author.id,
        event_type="post_approved",
        metadata={"post_id": str(post.id)},
    )

    return {
        "status": "success",
        "message": "Post approved successfully",
        "post_id": str(post.id),
    }


@router.post("/{pending_post_id}/reject/")
async def reject_pending_post_route(
    pending_post_id: UUID,
    background_tasks: BackgroundTasks,
    moderation_reason: str = Query(..., min_length=1),
    _: Any = Depends(get_admin_user),
) -> Dict[str, Any]:
    """
    Reject a pending post with a moderation reason.
    """
    # Get the pending post
    pending_post = await get_pending_post_by_id(pending_post_id)
    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending post not found",
        )

    # Reject the post
    rejected_post = await reject_pending_post(
        pending_post_id=pending_post_id,
        moderation_reason=moderation_reason,
    )
    if not rejected_post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject post",
        )

    # Log the event
    background_tasks.add_task(
        create_event,
        user_id=rejected_post.author.id,
        event_type="post_rejected",
        metadata={
            "post_id": str(rejected_post.id),
            "moderation_reason": moderation_reason,
        },
    )

    return {
        "status": "success",
        "message": "Post rejected successfully",
        "rejected_post_id": str(rejected_post.id),
    }
