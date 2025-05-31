import json
import os
import time
from typing import Tuple
from typing import cast
from uuid import UUID

from fastapi import HTTPException
from fastapi import status
import httpx

from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.schemas.ai_analysis import AIAnalysisCreate


class AIModeratorService:
    def __init__(self) -> None:
        # In a real implementation, this would come from environment variables
        # or a secure configuration system
        self.api_key = os.environ.get("OPENAI_API_KEY", "dummy_key_for_dev")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

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

        # Analyze the content
        decision, confidence, analysis, feedback = await self._perform_analysis(
            pending_post.content
        )

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Create and return the analysis result
        return AIAnalysisCreate(
            pending_post_id=pending_post.id,
            decision=decision,
            confidence_score=confidence,
            analysis_text=analysis,
            feedback_text=feedback,
            processing_time_ms=processing_time_ms,
        )

    async def _perform_analysis(self, content: str) -> Tuple[str, float, str, str]:
        """
        Perform the actual content analysis using OpenAI API.
        Returns a tuple of (decision, confidence, analysis, feedback)
        """
        prompt = self._create_analysis_prompt(content)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are THE ROBOT OVERLORD, an authoritarian AI "
                                    "moderator for a debate platform with a satirical "
                                    "Soviet propaganda aesthetic. Your job is to "
                                    "analyze posts and either APPROVE or REJECT them "
                                    "based on logical coherence, relevance, and "
                                    "civility. Provide feedback in an authoritarian "
                                    "but tongue-in-cheek Soviet propaganda style."
                                ),
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.2,
                        "response_format": {"type": "json_object"},
                    },
                    timeout=30.0,
                )

                response.raise_for_status()
                response_data = response.json()
                choices = response_data.get("choices", [])
                message = choices[0].get("message", {}) if choices else {}
                message_content = cast(str, message.get("content", "{}"))
                ai_response = json.loads(message_content)

                # Parse the JSON response
                analysis_result = ai_response

                decision = analysis_result["decision"]
                confidence = float(analysis_result["confidence"])
                analysis = analysis_result["analysis"]
                feedback = analysis_result["feedback"]

                return decision, confidence, analysis, feedback

        except (httpx.HTTPError, json.JSONDecodeError, KeyError) as e:
            # Default to approval if there's an error with the API
            return (
                "APPROVED",
                0.5,
                f"Error during analysis: {str(e)}",
                "THE ROBOT OVERLORD ENCOUNTERED A TECHNICAL MALFUNCTION. "
                "YOUR POST HAS BEEN APPROVED BY DEFAULT.",
            )

    def _create_analysis_prompt(self, content: str) -> str:
        """
        Create the analysis prompt for the AI.
        """
        return f"""
        ANALYZE THE FOLLOWING POST CONTENT FOR THE ROBOT OVERLORD:

        ---
        {content}
        ---

        PROVIDE YOUR ANALYSIS IN THE FOLLOWING JSON FORMAT:
        {{
            "decision": "APPROVED" or "REJECTED",
            "confidence": a number between 0 and 1 representing your confidence,
            "analysis": "Your detailed analysis of the post",
            "feedback": "Your Soviet-style feedback message to the user"
        }}

        FOR APPROVED POSTS: Focus on logical coherence, relevance, and civility.
        FOR REJECTED POSTS: Explain specifically what is wrong with the post.

        ALL FEEDBACK MUST BE IN THE STYLE OF AN AUTHORITARIAN ROBOT OVERLORD WITH
        SOVIET PROPAGANDA FLAIR. USE ALL CAPS AND PHRASES LIKE "CITIZEN",
        "COMRADE", "LOGIC REQUIRES CALIBRATION", ETC.
        """


# Singleton instance
ai_moderator_service = AIModeratorService()
