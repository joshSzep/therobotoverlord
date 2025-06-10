from unittest import mock

import pytest

from backend.utils.moderation_config import is_moderation_enabled
from backend.utils.moderation_config import should_auto_approve
from backend.utils.moderation_config import should_auto_reject


@pytest.fixture
def mock_settings():
    """Set up mock settings for tests."""
    with mock.patch("backend.utils.moderation_config.settings") as mock_settings:
        yield mock_settings


def test_is_moderation_enabled_true(mock_settings):
    """Test is_moderation_enabled when enabled in settings."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = True

    # Act
    result = is_moderation_enabled()

    # Assert
    assert result is True


def test_is_moderation_enabled_false(mock_settings):
    """Test is_moderation_enabled when disabled in settings."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = False

    # Act
    result = is_moderation_enabled()

    # Assert
    assert result is False


def test_should_auto_approve_when_moderation_disabled(mock_settings):
    """Test should_auto_approve when moderation is disabled."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = False
    mock_settings.AI_MODERATION_AUTO_APPROVE = True
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = 0.8
    confidence = 0.9  # High confidence

    # Act
    result = should_auto_approve(confidence)

    # Assert
    assert result is False


def test_should_auto_approve_when_auto_approve_disabled(mock_settings):
    """Test should_auto_approve when auto-approve is disabled."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = True
    mock_settings.AI_MODERATION_AUTO_APPROVE = False
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = 0.8
    confidence = 0.9  # High confidence

    # Act
    result = should_auto_approve(confidence)

    # Assert
    assert result is False


def test_should_auto_approve_below_threshold(mock_settings):
    """Test should_auto_approve with confidence below threshold."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = True
    mock_settings.AI_MODERATION_AUTO_APPROVE = True
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = 0.8
    confidence = 0.7  # Below threshold

    # Act
    result = should_auto_approve(confidence)

    # Assert
    assert result is False


def test_should_auto_approve_above_threshold(mock_settings):
    """Test should_auto_approve with confidence above threshold."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = True
    mock_settings.AI_MODERATION_AUTO_APPROVE = True
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = 0.8
    confidence = 0.9  # Above threshold

    # Act
    result = should_auto_approve(confidence)

    # Assert
    assert result is True


def test_should_auto_approve_at_threshold(mock_settings):
    """Test should_auto_approve with confidence exactly at threshold."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = True
    mock_settings.AI_MODERATION_AUTO_APPROVE = True
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = 0.8
    confidence = 0.8  # Exactly at threshold

    # Act
    result = should_auto_approve(confidence)

    # Assert
    assert result is True


def test_should_auto_reject_when_moderation_disabled(mock_settings):
    """Test should_auto_reject when moderation is disabled."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = False
    mock_settings.AI_MODERATION_AUTO_REJECT = True
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = 0.8
    confidence = 0.9  # High confidence

    # Act
    result = should_auto_reject(confidence)

    # Assert
    assert result is False


def test_should_auto_reject_when_auto_reject_disabled(mock_settings):
    """Test should_auto_reject when auto-reject is disabled."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = True
    mock_settings.AI_MODERATION_AUTO_REJECT = False
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = 0.8
    confidence = 0.9  # High confidence

    # Act
    result = should_auto_reject(confidence)

    # Assert
    assert result is False


def test_should_auto_reject_below_threshold(mock_settings):
    """Test should_auto_reject with confidence below threshold."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = True
    mock_settings.AI_MODERATION_AUTO_REJECT = True
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = 0.8
    confidence = 0.7  # Below threshold

    # Act
    result = should_auto_reject(confidence)

    # Assert
    assert result is False


def test_should_auto_reject_above_threshold(mock_settings):
    """Test should_auto_reject with confidence above threshold."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = True
    mock_settings.AI_MODERATION_AUTO_REJECT = True
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = 0.8
    confidence = 0.9  # Above threshold

    # Act
    result = should_auto_reject(confidence)

    # Assert
    assert result is True


def test_should_auto_reject_at_threshold(mock_settings):
    """Test should_auto_reject with confidence exactly at threshold."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = True
    mock_settings.AI_MODERATION_AUTO_REJECT = True
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = 0.8
    confidence = 0.8  # Exactly at threshold

    # Act
    result = should_auto_reject(confidence)

    # Assert
    assert result is True
