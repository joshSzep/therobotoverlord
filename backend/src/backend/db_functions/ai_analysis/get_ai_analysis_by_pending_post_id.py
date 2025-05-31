from uuid import UUID

from backend.db.models.ai_analysis import AIAnalysis
from backend.schemas.ai_analysis import AIAnalysisResponse


async def get_ai_analysis_by_pending_post_id(
    pending_post_id: UUID,
) -> AIAnalysisResponse:
    """
    Get the latest AI analysis for a pending post.
    """
    # Get the latest AI analysis for the pending post
    ai_analysis = (
        await AIAnalysis.filter(pending_post_id=pending_post_id)
        .order_by("-created_at")
        .first()
    )

    if not ai_analysis:
        raise ValueError(f"AI analysis for pending post {pending_post_id} not found")

    # Convert to schema
    return AIAnalysisResponse(
        id=ai_analysis.id,
        pending_post_id=ai_analysis.pending_post.id,
        decision=ai_analysis.decision,
        confidence_score=ai_analysis.confidence_score,
        analysis_text=ai_analysis.analysis_text,
        feedback_text=ai_analysis.feedback_text,
        processing_time_ms=ai_analysis.processing_time_ms,
        created_at=ai_analysis.created_at,
        updated_at=ai_analysis.updated_at,
    )
