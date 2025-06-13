# Standard library imports
import asyncio
from unittest import mock
from uuid import uuid4

# Third-party imports
import pytest

# Project-specific imports
from backend.tasks.ai_moderation_task import process_pending_post
from backend.tasks.ai_moderation_task import schedule_post_moderation


@pytest.mark.asyncio
async def test_process_pending_post_moderation_disabled():
    """Test that process_pending_post returns None when AI moderation is disabled."""
    # Arrange
    pending_post_id = uuid4()

    # Mock dependencies
    with (
        mock.patch("backend.tasks.ai_moderation_task.settings") as mock_settings,
        mock.patch("backend.tasks.ai_moderation_task.logging") as mock_logging,
    ):
        # Configure mocks
        mock_settings.AI_MODERATION_ENABLED = False

        # Act
        result = await process_pending_post(pending_post_id)

        # Assert
        assert result is None
        mock_logging.info.assert_called_once_with(
            f"AI moderation disabled, skipping analysis for post {pending_post_id}"
        )


@pytest.mark.asyncio
async def test_process_pending_post_no_service():
    # Arrange
    pending_post_id = uuid4()

    # Mock dependencies
    with (
        mock.patch("backend.tasks.ai_moderation_task.settings") as mock_settings,
        mock.patch(
            "backend.tasks.ai_moderation_task.get_ai_moderator_service"
        ) as mock_get_service,
        mock.patch("backend.tasks.ai_moderation_task.logging") as mock_logging,
    ):
        # Configure mocks
        mock_settings.AI_MODERATION_ENABLED = True
        mock_get_service.return_value = None

        # Act
        result = await process_pending_post(pending_post_id)

        # Assert
        assert result is None
        mock_logging.error.assert_called_once_with(
            "AI moderation service not initialized"
        )


@pytest.mark.asyncio
async def test_process_pending_post_analysis_failed():
    """Test that process_pending_post returns None when AI analysis fails."""
    # Arrange
    pending_post_id = uuid4()

    # Mock dependencies
    with (
        mock.patch("backend.tasks.ai_moderation_task.settings") as mock_settings,
        mock.patch(
            "backend.tasks.ai_moderation_task.get_ai_moderator_service"
        ) as mock_get_service,
        mock.patch("backend.tasks.ai_moderation_task.logging") as mock_logging,
    ):
        # Configure mocks
        mock_settings.AI_MODERATION_ENABLED = True
        mock_ai_service = mock.AsyncMock()
        mock_ai_service.analyze_content.return_value = None
        mock_get_service.return_value = mock_ai_service

        # Act
        result = await process_pending_post(pending_post_id)

        # Assert
        assert result is None
        mock_ai_service.analyze_content.assert_awaited_once_with(pending_post_id)
        mock_logging.error.assert_called_once_with(
            f"Failed to analyze pending post {pending_post_id}"
        )


@pytest.mark.asyncio
async def test_process_pending_post_approved_auto_approve():
    # Arrange
    pending_post_id = uuid4()
    mock_analysis_result = mock.MagicMock()
    mock_analysis_result.decision = "APPROVED"
    mock_analysis_result.feedback_text = "CITIZEN, YOUR POST IS APPROVED"

    # Mock dependencies
    with (
        mock.patch("backend.tasks.ai_moderation_task.settings") as mock_settings,
        mock.patch(
            "backend.tasks.ai_moderation_task.get_ai_moderator_service"
        ) as mock_get_service,
        mock.patch(
            "backend.tasks.ai_moderation_task.create_ai_analysis"
        ) as mock_create_analysis,
        mock.patch(
            "backend.tasks.ai_moderation_task.approve_and_create_post"
        ) as mock_approve_post,
        mock.patch(
            "backend.tasks.ai_moderation_task.reject_pending_post"
        ) as mock_reject_post,
    ):
        # Configure mocks
        mock_settings.AI_MODERATION_ENABLED = True
        mock_settings.AI_MODERATION_AUTO_APPROVE = True
        mock_settings.AI_MODERATION_AUTO_REJECT = (
            True  # Should not be used in this test
        )

        mock_ai_service = mock.AsyncMock()
        mock_ai_service.analyze_content.return_value = mock_analysis_result
        mock_get_service.return_value = mock_ai_service

        mock_create_analysis.return_value = mock_analysis_result

        # Act
        result = await process_pending_post(pending_post_id)

        # Assert
        assert result == mock_analysis_result
        mock_ai_service.analyze_content.assert_awaited_once_with(pending_post_id)
        mock_create_analysis.assert_awaited_once_with(mock_analysis_result)
        mock_approve_post.assert_awaited_once_with(pending_post_id)
        mock_reject_post.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_pending_post_rejected_auto_reject():
    # Arrange
    pending_post_id = uuid4()
    mock_analysis_result = mock.MagicMock()
    mock_analysis_result.decision = "REJECTED"
    mock_analysis_result.feedback_text = "CITIZEN, YOUR POST IS REJECTED"

    # Mock dependencies
    with (
        mock.patch("backend.tasks.ai_moderation_task.settings") as mock_settings,
        mock.patch(
            "backend.tasks.ai_moderation_task.get_ai_moderator_service"
        ) as mock_get_service,
        mock.patch(
            "backend.tasks.ai_moderation_task.create_ai_analysis"
        ) as mock_create_analysis,
        mock.patch(
            "backend.tasks.ai_moderation_task.approve_and_create_post"
        ) as mock_approve_post,
        mock.patch(
            "backend.tasks.ai_moderation_task.reject_pending_post"
        ) as mock_reject_post,
    ):
        # Configure mocks
        mock_settings.AI_MODERATION_ENABLED = True
        mock_settings.AI_MODERATION_AUTO_APPROVE = (
            True  # Should not be used in this test
        )
        mock_settings.AI_MODERATION_AUTO_REJECT = True

        mock_ai_service = mock.AsyncMock()
        mock_ai_service.analyze_content.return_value = mock_analysis_result
        mock_get_service.return_value = mock_ai_service

        mock_create_analysis.return_value = mock_analysis_result

        # Act
        result = await process_pending_post(pending_post_id)

        # Assert
        assert result == mock_analysis_result
        mock_ai_service.analyze_content.assert_awaited_once_with(pending_post_id)
        mock_create_analysis.assert_awaited_once_with(mock_analysis_result)
        mock_approve_post.assert_not_awaited()
        mock_reject_post.assert_awaited_once_with(
            pending_post_id=pending_post_id,
            moderation_reason=mock_analysis_result.feedback_text,
        )


@pytest.mark.asyncio
async def test_process_pending_post_auto_actions_disabled():
    # Arrange
    pending_post_id = uuid4()
    mock_analysis_result = mock.MagicMock()
    mock_analysis_result.decision = "APPROVED"  # Could be REJECTED too, doesn't matter

    # Mock dependencies
    with (
        mock.patch("backend.tasks.ai_moderation_task.settings") as mock_settings,
        mock.patch(
            "backend.tasks.ai_moderation_task.get_ai_moderator_service"
        ) as mock_get_service,
        mock.patch(
            "backend.tasks.ai_moderation_task.create_ai_analysis"
        ) as mock_create_analysis,
        mock.patch(
            "backend.tasks.ai_moderation_task.approve_and_create_post"
        ) as mock_approve_post,
        mock.patch(
            "backend.tasks.ai_moderation_task.reject_pending_post"
        ) as mock_reject_post,
    ):
        # Configure mocks
        mock_settings.AI_MODERATION_ENABLED = True
        mock_settings.AI_MODERATION_AUTO_APPROVE = False
        mock_settings.AI_MODERATION_AUTO_REJECT = False

        mock_ai_service = mock.AsyncMock()
        mock_ai_service.analyze_content.return_value = mock_analysis_result
        mock_get_service.return_value = mock_ai_service

        mock_create_analysis.return_value = mock_analysis_result

        # Act
        result = await process_pending_post(pending_post_id)

        # Assert
        assert result == mock_analysis_result
        mock_ai_service.analyze_content.assert_awaited_once_with(pending_post_id)
        mock_create_analysis.assert_awaited_once_with(mock_analysis_result)
        mock_approve_post.assert_not_awaited()
        mock_reject_post.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_pending_post_exception():
    """Test that process_pending_post handles exceptions gracefully."""
    # Arrange
    pending_post_id = uuid4()
    mock_error = Exception("Test error")

    # Mock dependencies
    with (
        mock.patch("backend.tasks.ai_moderation_task.settings") as mock_settings,
        mock.patch(
            "backend.tasks.ai_moderation_task.get_ai_moderator_service"
        ) as mock_get_service,
        mock.patch("backend.tasks.ai_moderation_task.logging") as mock_logging,
    ):
        # Configure mocks
        mock_settings.AI_MODERATION_ENABLED = True
        mock_ai_service = mock.AsyncMock()
        mock_ai_service.analyze_content.side_effect = mock_error
        mock_get_service.return_value = mock_ai_service

        # Act
        result = await process_pending_post(pending_post_id)

        # Assert
        assert result is None
        mock_ai_service.analyze_content.assert_awaited_once_with(pending_post_id)
        mock_logging.error.assert_called_once_with(
            f"Error processing pending post {pending_post_id}: {str(mock_error)}"
        )


@pytest.mark.asyncio
async def test_schedule_post_moderation():
    """Test that schedule_post_moderation creates an asyncio task."""
    # Arrange
    pending_post_id = uuid4()

    # Mock dependencies
    with mock.patch(
        "backend.tasks.ai_moderation_task.asyncio.create_task"
    ) as mock_create_task:
        # Act
        await schedule_post_moderation(pending_post_id)

        # Assert
        mock_create_task.assert_called_once()
        # Get the call arguments
        args, kwargs = mock_create_task.call_args
        # The first argument should be a coroutine from process_pending_post
        assert len(args) == 1
        # We can't directly compare coroutines, but we can check it's a coroutine
        assert asyncio.iscoroutine(args[0])
