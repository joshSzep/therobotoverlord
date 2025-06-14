from unittest import mock
import uuid

import pytest

from backend.db.models.ai_analysis import AIAnalysis
from backend.db_functions.ai_analysis.create_ai_analysis import create_ai_analysis
from backend.schemas.ai_analysis import AIAnalysisCreate
from backend.schemas.ai_analysis import AIAnalysisResponse


@pytest.fixture
def analysis_data() -> AIAnalysisCreate:
    return AIAnalysisCreate(
        pending_post_id=uuid.uuid4(),
        decision="APPROVED",
        confidence_score=0.95,
        analysis_text="great post",
        feedback_text="good job",
        processing_time_ms=123,
    )


@pytest.fixture
def mock_ai_analysis(analysis_data: AIAnalysisCreate) -> mock.MagicMock:
    ai = mock.MagicMock(spec=AIAnalysis)
    ai.id = uuid.uuid4()
    ai.decision = analysis_data.decision
    ai.confidence_score = analysis_data.confidence_score
    ai.analysis_text = analysis_data.analysis_text
    ai.feedback_text = analysis_data.feedback_text
    ai.processing_time_ms = analysis_data.processing_time_ms
    ai.created_at = mock.MagicMock()
    ai.updated_at = mock.MagicMock()
    ai.pending_post_id = analysis_data.pending_post_id
    return ai


@pytest.mark.asyncio
async def test_create_ai_analysis_success(analysis_data, mock_ai_analysis) -> None:
    with mock.patch.object(
        AIAnalysis, "create", new=mock.AsyncMock(return_value=mock_ai_analysis)
    ) as mock_create:
        result = await create_ai_analysis(analysis_data)

        assert isinstance(result, AIAnalysisResponse)
        assert result.pending_post_id == analysis_data.pending_post_id
        assert result.decision == analysis_data.decision
        assert result.confidence_score == analysis_data.confidence_score
        mock_create.assert_called_once_with(
            pending_post_id=analysis_data.pending_post_id,
            decision=analysis_data.decision,
            confidence_score=analysis_data.confidence_score,
            analysis_text=analysis_data.analysis_text,
            feedback_text=analysis_data.feedback_text,
            processing_time_ms=analysis_data.processing_time_ms,
        )
