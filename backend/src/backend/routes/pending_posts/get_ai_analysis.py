from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import status

from backend.db.models.user import User
from backend.db_functions.ai_analysis.get_ai_analysis_by_pending_post_id import (
    get_ai_analysis_by_pending_post_id,
)
from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.schemas.ai_analysis import AIAnalysisResponse
from backend.utils.auth import get_current_user

# Create router
router = APIRouter()


@router.get("/{pending_post_id}/analysis/", response_model=AIAnalysisResponse)
async def get_ai_analysis(
    pending_post_id: UUID = Path(
        ..., description="The ID of the pending post to get analysis for"
    ),
    current_user: User = Depends(get_current_user),
) -> AIAnalysisResponse:
    # First check if the pending post exists
    pending_post = await get_pending_post_by_id(pending_post_id)
    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending post not found",
        )

    # Check if the user is the author of the pending post
    if str(pending_post.author.id) != str(current_user.id):
        # Only allow the author to see their own pending post analysis
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this analysis",
        )

    try:
        # Get the AI analysis for the pending post
        analysis = await get_ai_analysis_by_pending_post_id(pending_post_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI analysis not found for this pending post",
            )
        return analysis
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        # Log the error
        import logging

        logging.error(f"Error getting AI analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving AI analysis: {str(e)}",
        )
