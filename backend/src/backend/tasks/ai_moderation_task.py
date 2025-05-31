import asyncio
import logging
from typing import Optional
from uuid import UUID

from backend.db_functions.ai_analysis.create_ai_analysis import create_ai_analysis
from backend.db_functions.pending_posts.approve_and_create_post import (
    approve_and_create_post,
)
from backend.db_functions.pending_posts.reject_pending_post import reject_pending_post
from backend.schemas.ai_analysis import AIAnalysisResponse
from backend.utils.ai_moderation import get_ai_moderator_service
from backend.utils.settings import settings


async def process_pending_post(pending_post_id: UUID) -> Optional[AIAnalysisResponse]:
    """
    Process a pending post through the AI moderation pipeline.
    This is run as a background task.
    """
    # Skip moderation if disabled in settings
    if not settings.AI_MODERATION_ENABLED:
        logging.info(
            f"AI moderation disabled, skipping analysis for post {pending_post_id}"
        )
        return None

    try:
        # Get the AI moderation service
        ai_service = get_ai_moderator_service()
        if not ai_service:
            logging.error("AI moderation service not initialized")
            return None

        # Analyze the content
        analysis_result = await ai_service.analyze_content(pending_post_id)
        if not analysis_result:
            logging.error(f"Failed to analyze pending post {pending_post_id}")
            return None

        # Store the analysis result
        analysis = await create_ai_analysis(analysis_result)

        # Take action based on the decision and settings
        if (
            analysis_result.decision == "APPROVED"
            and settings.AI_MODERATION_AUTO_APPROVE
        ):
            # Auto-approve the post if enabled
            await approve_and_create_post(pending_post_id)
        elif (
            analysis_result.decision == "REJECTED"
            and settings.AI_MODERATION_AUTO_REJECT
        ):
            # Auto-reject the post if enabled
            await reject_pending_post(
                pending_post_id=pending_post_id,
                moderation_reason=analysis_result.feedback_text,
            )

        return analysis
    except Exception as e:
        # Log the error but don't crash
        logging.error(f"Error processing pending post {pending_post_id}: {str(e)}")
        return None


async def schedule_post_moderation(pending_post_id: UUID) -> None:
    """
    Schedule a pending post for moderation.
    This function can be called directly after creating a pending post.
    """
    # Create a task to process the pending post
    # We use asyncio.create_task to run this in the background
    asyncio.create_task(process_pending_post(pending_post_id))
