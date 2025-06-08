"""
Get post approval event for a pending post.
"""

import logging
from typing import Optional
from uuid import UUID

from backend.converters.user_event_to_schema import user_event_to_schema
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventResponse

logger = logging.getLogger(__name__)


async def get_post_approval_event(pending_post_id: UUID) -> Optional[UserEventResponse]:
    """
    Get the post approval event for a specific pending post.

    This function searches for a user event with event_type 'post_approval'
    that references the given pending post ID in its metadata.

    Args:
        pending_post_id: UUID of the pending post

    Returns:
        UserEventResponse if found, None otherwise
    """
    try:
        # Look for a post_approval event that references this pending post
        event = await UserEvent.filter(
            event_type="post_approval",
            metadata__contains={"pending_post_id": str(pending_post_id)},
        ).first()

        if not event:
            logger.debug(f"No approval event found for pending post {pending_post_id}")
            return None

        return await user_event_to_schema(event)

    except Exception as e:
        logger.error(
            f"Error finding approval event for pending post {pending_post_id}: {e}"
        )
        return None
