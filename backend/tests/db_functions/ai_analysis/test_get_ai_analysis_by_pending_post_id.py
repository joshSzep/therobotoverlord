from unittest import mock
import uuid

import pytest

from backend.db.models.ai_analysis import AIAnalysis
from backend.db_functions.ai_analysis.get_ai_analysis_by_pending_post_id import (
    get_ai_analysis_by_pending_post_id,
)
from backend.schemas.ai_analysis import AIAnalysisResponse


@pytest.fixture
def mock_ai_analysis() -> mock.MagicMock:
    ai = mock.MagicMock(spec=AIAnalysis)
    ai.id = uuid.uuid4()
    ai.pending_post = mock.MagicMock(id=uuid.uuid4())
    ai.decision = "REJECTED"
    ai.confidence_score = 0.7
    ai.analysis_text = "bad"
    ai.feedback_text = "no"
    ai.processing_time_ms = 50
    ai.created_at = mock.MagicMock()
    ai.updated_at = mock.MagicMock()
    return ai


@pytest.mark.asyncio
async def test_get_ai_analysis_by_pending_post_id_success(mock_ai_analysis) -> None:
    qs = mock.MagicMock()
    qs.order_by.return_value.first = mock.AsyncMock(return_value=mock_ai_analysis)
    with mock.patch.object(AIAnalysis, "filter", return_value=qs) as mock_filter:
        result = await get_ai_analysis_by_pending_post_id(
            mock_ai_analysis.pending_post.id
        )

        assert isinstance(result, AIAnalysisResponse)
        assert result.id == mock_ai_analysis.id
        mock_filter.assert_called_once_with(
            pending_post_id=mock_ai_analysis.pending_post.id
        )
        qs.order_by.assert_called_once_with("-created_at")
        qs.order_by.return_value.first.assert_called_once()


@pytest.mark.asyncio
async def test_get_ai_analysis_by_pending_post_id_not_found() -> None:
    qs = mock.MagicMock()
    qs.order_by.return_value.first = mock.AsyncMock(return_value=None)
    with mock.patch.object(AIAnalysis, "filter", return_value=qs) as mock_filter:
        with pytest.raises(ValueError):
            await get_ai_analysis_by_pending_post_id(uuid.uuid4())
        qs.order_by.assert_called_once_with("-created_at")
        qs.order_by.return_value.first.assert_called_once()
        mock_filter.assert_called_once()
