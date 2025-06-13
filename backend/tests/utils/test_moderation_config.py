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


def test_moderation_config_loading(mock_settings):
    """Test that moderation configuration is loaded correctly from settings."""
    # Arrange
    expected_enabled = True
    expected_auto_approve = True
    expected_auto_reject = False
    expected_threshold = 0.75

    mock_settings.AI_MODERATION_ENABLED = expected_enabled
    mock_settings.AI_MODERATION_AUTO_APPROVE = expected_auto_approve
    mock_settings.AI_MODERATION_AUTO_REJECT = expected_auto_reject
    mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = expected_threshold

    # Act & Assert
    assert is_moderation_enabled() == expected_enabled

    # Test auto-approve with threshold
    assert should_auto_approve(expected_threshold) is True
    assert should_auto_approve(expected_threshold - 0.01) is False

    # Test auto-reject with threshold
    # Because auto_reject is False
    assert should_auto_reject(expected_threshold) is False

    # Change auto_reject setting
    mock_settings.AI_MODERATION_AUTO_REJECT = True
    assert should_auto_reject(expected_threshold) is True
    assert should_auto_reject(expected_threshold - 0.01) is False


def test_default_values_fallback(mock_settings):
    """Test that the module handles missing configuration values gracefully."""
    # Arrange - simulate settings without the required attributes
    delattr(mock_settings, "AI_MODERATION_ENABLED")
    delattr(mock_settings, "AI_MODERATION_AUTO_APPROVE")
    delattr(mock_settings, "AI_MODERATION_AUTO_REJECT")
    delattr(mock_settings, "AI_MODERATION_CONFIDENCE_THRESHOLD")

    # Add default values via __getattr__
    type(mock_settings).__getattr__ = lambda self, name: {
        "AI_MODERATION_ENABLED": False,
        "AI_MODERATION_AUTO_APPROVE": False,
        "AI_MODERATION_AUTO_REJECT": False,
        "AI_MODERATION_CONFIDENCE_THRESHOLD": 0.9,
    }.get(name)

    # Act & Assert
    assert is_moderation_enabled() is False
    assert should_auto_approve(1.0) is False  # Even with 100% confidence
    assert should_auto_reject(1.0) is False  # Even with 100% confidence

    # Now enable moderation but keep auto-approve/reject disabled
    type(mock_settings).__getattr__ = lambda self, name: {
        "AI_MODERATION_ENABLED": True,
        "AI_MODERATION_AUTO_APPROVE": False,
        "AI_MODERATION_AUTO_REJECT": False,
        "AI_MODERATION_CONFIDENCE_THRESHOLD": 0.9,
    }.get(name)

    assert is_moderation_enabled() is True
    assert should_auto_approve(1.0) is False  # Still False because auto-approve is off
    assert should_auto_reject(1.0) is False  # Still False because auto-reject is off


def test_configuration_validation(mock_settings):
    """Test that the module correctly validates configuration values."""
    # Arrange
    mock_settings.AI_MODERATION_ENABLED = True
    mock_settings.AI_MODERATION_AUTO_APPROVE = True
    mock_settings.AI_MODERATION_AUTO_REJECT = True

    # Test with valid threshold values
    for threshold in [0.0, 0.5, 0.75, 1.0]:
        mock_settings.AI_MODERATION_CONFIDENCE_THRESHOLD = threshold

        # These should not raise exceptions
        is_moderation_enabled()
        should_auto_approve(0.5)
        should_auto_reject(0.5)

    # Test with invalid confidence values
    for invalid_confidence in [-0.1, 1.1, 2.0]:
        # These functions should handle invalid inputs gracefully
        # For now, we're just testing that they don't raise exceptions
        # In a real implementation, you might want to add input validation
        should_auto_approve(invalid_confidence)
        should_auto_reject(invalid_confidence)
