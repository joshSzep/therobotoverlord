from backend.db.models.ai_analysis import AIAnalysis
from backend.schemas.ai_analysis import AIAnalysisCreate
from backend.schemas.ai_analysis import AIAnalysisResponse


async def create_ai_analysis(
    analysis_data: AIAnalysisCreate,
) -> AIAnalysisResponse:
    """
    Create a new AI analysis record.
    """
    # Create the AI analysis
    ai_analysis = await AIAnalysis.create(
        pending_post_id=analysis_data.pending_post_id,
        decision=analysis_data.decision,
        confidence_score=analysis_data.confidence_score,
        analysis_text=analysis_data.analysis_text,
        feedback_text=analysis_data.feedback_text,
        processing_time_ms=analysis_data.processing_time_ms,
    )

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
