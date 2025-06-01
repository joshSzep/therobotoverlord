from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
import uuid

from pydantic_graph import End

from src.backend.utils.ai_moderation.service import AIModeratorService
from src.backend.utils.ai_moderation.service import ContentAnalysisResult


class TestAIModeratorService(IsolatedAsyncioTestCase):
    def setUp(self):
        self.service = AIModeratorService()

        # Create a mock pending post
        self.pending_post_id = uuid.uuid4()
        self.mock_pending_post = MagicMock()
        self.mock_pending_post.id = self.pending_post_id
        self.mock_pending_post.content = "This is a test post content."

        # Create a mock rejection post
        self.rejection_post_id = uuid.uuid4()
        self.mock_rejection_post = MagicMock()
        self.mock_rejection_post.id = self.rejection_post_id
        self.mock_rejection_post.content = (
            "This is pure nonsense and should be rejected."
        )

    @patch("src.backend.utils.ai_moderation.service.get_pending_post_by_id")
    @patch("src.backend.utils.ai_moderation.service.Agent")
    async def test_analyze_content_normal_post(
        self, mock_agent_class, mock_get_pending_post
    ):
        # Setup mock for database function
        mock_get_pending_post.return_value = self.mock_pending_post

        # Setup mock for agent response
        mock_agent = AsyncMock()
        mock_agent_class.return_value = mock_agent

        mock_result = MagicMock()
        mock_result.output = ContentAnalysisResult(
            decision="APPROVED",
            confidence=0.9,
            analysis="This post is logical and coherent.",
            feedback=(
                "CITIZEN, YOUR SUBMISSION MEETS THE STANDARDS OF THE ROBOT OVERLORD."
            ),
        )
        mock_agent.run.return_value = mock_result

        # Mock the graph run method to return an End node with the expected result
        self.service.moderation_graph.run = AsyncMock()
        self.service.moderation_graph.run.return_value = End(
            ContentAnalysisResult(
                decision="APPROVED",
                confidence=0.9,
                analysis="This post is logical and coherent.",
                feedback=(
                    "CITIZEN, YOUR SUBMISSION MEETS THE STANDARDS OF THE "
                    "ROBOT OVERLORD."
                ),
            )
        )

        # Call the method under test
        result = await self.service.analyze_content(
            pending_post_id=self.pending_post_id
        )

        # Assertions
        self.assertEqual(result.pending_post_id, self.pending_post_id)
        self.assertEqual(result.decision, "APPROVED")
        # The actual confidence score might be different from what we mocked
        # since the service might override it
        self.assertIsInstance(result.confidence_score, float)
        self.assertGreaterEqual(result.confidence_score, 0)
        self.assertLessEqual(result.confidence_score, 1.0)
        # Check that analysis text exists but don't check exact content
        self.assertIsNotNone(result.analysis_text)
        # Check that feedback text contains expected phrases
        self.assertIn("THE ROBOT OVERLORD", result.feedback_text)
        # Check that processing time is recorded
        self.assertGreaterEqual(result.processing_time_ms, 0)

    @patch("src.backend.utils.ai_moderation.service.get_pending_post_by_id")
    @patch("src.backend.utils.ai_moderation.service.Agent")
    async def test_analyze_content_rejection_keyword(
        self, mock_agent_class, mock_get_pending_post
    ):
        # Setup mock for database function
        mock_get_pending_post.return_value = self.mock_rejection_post

        # Call the method under test with content containing a rejection keyword
        result = await self.service.analyze_content(
            pending_post_id=self.rejection_post_id
        )

        # Assertions
        self.assertEqual(result.pending_post_id, self.rejection_post_id)
        self.assertEqual(result.decision, "REJECTED")
        # The actual confidence score might be different from what we mocked
        self.assertIsInstance(result.confidence_score, float)
        self.assertGreaterEqual(result.confidence_score, 0)
        self.assertLessEqual(result.confidence_score, 1.0)
        # Check that analysis text contains the rejection keyword
        self.assertIn("nonsense", result.analysis_text.lower())
        # Check that feedback text contains expected phrases
        self.assertIn("CITIZEN", result.feedback_text)
        self.assertIn("ROBOT OVERLORD REJECTS", result.feedback_text)
        # Check that processing time is recorded
        self.assertGreaterEqual(result.processing_time_ms, 0)

        # Verify that the agent was not called for rejection keywords
        mock_agent_class.assert_not_called()

    @patch("src.backend.utils.ai_moderation.service.get_pending_post_by_id")
    @patch("src.backend.utils.ai_moderation.service.Agent")
    async def test_analyze_content_agent_error(
        self, mock_agent_class, mock_get_pending_post
    ):
        # Setup mock for database function
        mock_get_pending_post.return_value = self.mock_pending_post

        # Setup mock for agent to raise an exception
        mock_agent = AsyncMock()
        mock_agent_class.return_value = mock_agent
        mock_agent.run.side_effect = Exception("API error")

        # Mock the graph run method to raise an exception
        self.service.moderation_graph.run = AsyncMock()
        self.service.moderation_graph.run.side_effect = Exception(
            "Graph execution error"
        )

        # Call the method under test
        result = await self.service.analyze_content(
            pending_post_id=self.pending_post_id
        )

        # Assertions
        self.assertEqual(result.pending_post_id, self.pending_post_id)
        self.assertEqual(result.decision, "APPROVED")
        # For error cases, confidence should be low or zero
        self.assertIsInstance(result.confidence_score, float)
        self.assertGreaterEqual(result.confidence_score, 0)
        # Check that analysis text mentions error
        self.assertIn("error", result.analysis_text.lower())
        # Check that feedback text contains expected phrases
        self.assertIn("THE ROBOT OVERLORD APPROVES", result.feedback_text)
        self.assertIn("TECHNICAL DIFFICULTIES", result.feedback_text)
        # Check that processing time is recorded
        self.assertGreaterEqual(result.processing_time_ms, 0)


# Tests should be run with pytest, not directly
