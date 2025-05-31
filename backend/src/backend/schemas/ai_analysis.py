from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class AIAnalysisBase(BaseModel):
    decision: str = Field(
        ..., description="AI moderation decision: APPROVED or REJECTED"
    )
    confidence_score: float = Field(
        ..., description="Confidence score of the AI decision"
    )
    analysis_text: str = Field(..., description="Detailed analysis of the content")
    feedback_text: str = Field(..., description="Soviet-style feedback for the user")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class AIAnalysisCreate(AIAnalysisBase):
    pending_post_id: UUID = Field(
        ..., description="ID of the pending post being analyzed"
    )


class AIAnalysisResponse(AIAnalysisBase):
    id: UUID
    pending_post_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
