from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import status

from backend.db.models.user import User
from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.schemas.ai_analysis import AIAnalysisResponse
from backend.tasks.ai_moderation_task import process_pending_post
from backend.utils.auth import get_current_user

# Create router
router = APIRouter()


@router.post("/{pending_post_id}/moderate/", response_model=AIAnalysisResponse)
async def trigger_ai_moderation(
    pending_post_id: UUID = Path(
        ..., description="The ID of the pending post to moderate"
    ),
    current_user: User = Depends(get_current_user),
) -> AIAnalysisResponse:
    """
    Manually trigger AI moderation for a pending post.
    This endpoint is for admin use only.
    """
    # First check if the pending post exists
    pending_post = await get_pending_post_by_id(pending_post_id)
    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending post not found",
        )

    try:
        # Process the pending post through the AI moderation pipeline
        analysis = await process_pending_post(pending_post_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process pending post through AI moderation",
            )
        return analysis
    except Exception as e:
        # Log the error
        import logging

        logging.error(f"Error triggering AI moderation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering AI moderation: {str(e)}",
        )
