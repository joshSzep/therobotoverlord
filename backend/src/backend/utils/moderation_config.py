# Standard library imports

# Third-party imports

# Project-specific imports
from backend.utils.settings import settings


def is_moderation_enabled() -> bool:
    """
    Check if AI moderation is enabled in the application settings.

    Returns:
        bool: True if moderation is enabled, False otherwise
    """
    return settings.AI_MODERATION_ENABLED


def should_auto_approve(confidence: float) -> bool:
    """
    Determine if a post should be automatically approved based on settings and
    confidence.

    Args:
        confidence: The confidence score from the AI moderation (0.0 to 1.0)

    Returns:
        bool: True if the post should be auto-approved, False otherwise
    """
    if not is_moderation_enabled() or not settings.AI_MODERATION_AUTO_APPROVE:
        return False

    return confidence >= settings.AI_MODERATION_CONFIDENCE_THRESHOLD


def should_auto_reject(confidence: float) -> bool:
    """
    Determine if a post should be automatically rejected based on settings and
    confidence.

    Args:
        confidence: The confidence score from the AI moderation (0.0 to 1.0)

    Returns:
        bool: True if the post should be auto-rejected, False otherwise
    """
    if not is_moderation_enabled() or not settings.AI_MODERATION_AUTO_REJECT:
        return False

    return confidence >= settings.AI_MODERATION_CONFIDENCE_THRESHOLD
