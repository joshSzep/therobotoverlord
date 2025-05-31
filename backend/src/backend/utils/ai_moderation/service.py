from dataclasses import dataclass
import os
import time
from typing import Literal
from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from pydantic import Field
from pydantic_ai import Agent
from pydantic_graph import BaseNode
from pydantic_graph import End
from pydantic_graph import Graph
from pydantic_graph import GraphRunContext

from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.schemas.ai_analysis import AIAnalysisCreate


# Define the Pydantic models for the AI analysis results
class ContentAnalysisResult(BaseModel):
    decision: Literal["APPROVED", "REJECTED"] = Field(
        ..., description="AI moderation decision: APPROVED or REJECTED"
    )
    confidence: float = Field(..., description="Confidence score between 0 and 1")
    analysis: str = Field(..., description="Detailed analysis of the content")
    feedback: str = Field(..., description="Soviet-style feedback for the user")


# Define the state for the moderation workflow
@dataclass
class ModerationState:
    content: str
    pending_post_id: UUID
    start_time: float


# Define the nodes for the moderation workflow
@dataclass
class AnalyzeContent(BaseNode[ModerationState, None, ContentAnalysisResult]):
    async def run(
        self, ctx: GraphRunContext[ModerationState]
    ) -> End[ContentAnalysisResult]:
        # Create the AI agent for content analysis
        analysis_agent = Agent(
            "openai:gpt-4o",
            output_type=ContentAnalysisResult,
            system_prompt=(
                "You are THE ROBOT OVERLORD, an authoritarian AI "
                "moderator for a debate platform with a satirical "
                "Soviet propaganda aesthetic. Your job is to "
                "analyze posts and either APPROVE or REJECT them "
                "based on logical coherence, relevance, and "
                "civility. Provide feedback in an authoritarian "
                "but tongue-in-cheek Soviet propaganda style."
            ),
        )

        # Create the prompt for analysis
        prompt = f"""
        ANALYZE THE FOLLOWING POST CONTENT FOR THE ROBOT OVERLORD:

        ---
        {ctx.state.content}
        ---

        FOR APPROVED POSTS: Focus on logical coherence, relevance, and civility.
        FOR REJECTED POSTS: Explain specifically what is wrong with the post.

        ALL FEEDBACK MUST BE IN THE STYLE OF AN AUTHORITARIAN ROBOT OVERLORD WITH
        SOVIET PROPAGANDA FLAIR. USE ALL CAPS AND PHRASES LIKE "CITIZEN",
        "COMRADE", "LOGIC REQUIRES CALIBRATION", ETC.
        """

        try:
            # Run the analysis
            result = await analysis_agent.run(prompt)
            return End(result.output)
        except Exception as e:
            # Default to approval if there's an error with the API
            return End(
                ContentAnalysisResult(
                    decision="APPROVED",
                    confidence=0.5,
                    analysis=f"Error during analysis: {str(e)}",
                    feedback=(
                        "THE ROBOT OVERLORD ENCOUNTERED A TECHNICAL MALFUNCTION. "
                        "YOUR POST HAS BEEN APPROVED BY DEFAULT."
                    ),
                )
            )


class AIModeratorService:
    def __init__(self) -> None:
        # Initialize the moderation graph
        self.moderation_graph = Graph(nodes=(AnalyzeContent,))

        # Set API key from environment
        os.environ.setdefault(
            "OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", "dummy_key_for_dev")
        )

    async def analyze_content(self, pending_post_id: UUID) -> AIAnalysisCreate:
        """
        Analyze the content of a pending post and make a moderation decision.
        """
        # Get the pending post
        pending_post = await get_pending_post_by_id(pending_post_id)
        if not pending_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pending post not found",
            )

        # Start timing
        start_time = time.time()

        # Set up the state for the moderation workflow
        state = ModerationState(
            content=pending_post.content,
            pending_post_id=pending_post_id,
            start_time=start_time,
        )

        # Run the moderation workflow
        result = await self.moderation_graph.run(AnalyzeContent(), state=state)
        analysis_result = result.output

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Create and return the analysis result
        return AIAnalysisCreate(
            pending_post_id=pending_post.id,
            decision=analysis_result.decision,
            confidence_score=analysis_result.confidence,
            analysis_text=analysis_result.analysis,
            feedback_text=analysis_result.feedback,
            processing_time_ms=processing_time_ms,
        )


# Singleton instance
ai_moderator_service = AIModeratorService()
