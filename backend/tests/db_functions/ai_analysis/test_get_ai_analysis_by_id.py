from unittest import mock
import uuid

import pytest

from backend.db.models.ai_analysis import AIAnalysis
from backend.db_functions.ai_analysis.get_ai_analysis_by_id import get_ai_analysis_by_id
from backend.schemas.ai_analysis import AIAnalysisResponse


@pytest.fixture
def mock_ai_analysis() -> mock.MagicMock:
    ai = mock.MagicMock(spec=AIAnalysis)
    ai.id = uuid.uuid4()
    ai.pending_post = mock.MagicMock(id=uuid.uuid4())
    ai.decision = "APPROVED"
    ai.confidence_score = 0.9
    ai.analysis_text = "analysis"
    ai.feedback_text = "feedback"
    ai.processing_time_ms = 50
    ai.created_at = mock.MagicMock()
    ai.updated_at = mock.MagicMock()
    return ai


@pytest.mark.asyncio
async def test_get_ai_analysis_by_id_success(mock_ai_analysis) -> None:
    with mock.patch.object(
        AIAnalysis, "get_or_none", new=mock.AsyncMock(return_value=mock_ai_analysis)
    ) as mock_get:
        result = await get_ai_analysis_by_id(mock_ai_analysis.id)

        assert isinstance(result, AIAnalysisResponse)
        assert result.id == mock_ai_analysis.id
        assert result.pending_post_id == mock_ai_analysis.pending_post.id
        mock_get.assert_called_once_with(id=mock_ai_analysis.id)


@pytest.mark.asyncio
async def test_get_ai_analysis_by_id_not_found() -> None:
    analysis_id = uuid.uuid4()
    with mock.patch.object(
        AIAnalysis, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        with pytest.raises(ValueError):
            await get_ai_analysis_by_id(analysis_id)
        mock_get.assert_called_once_with(id=analysis_id)
