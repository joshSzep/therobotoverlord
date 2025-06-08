"""
Create a post approval event to track the relationship between a pending post and its
approved post.
"""

import logging
from typing import Any
from typing import Dict
from typing import Optional
from uuid import UUID

from backend.db_functions.user_events.create_event import create_event
from backend.schemas.user_event import UserEventResponse

logger = logging.getLogger(__name__)


async def create_post_approval_event(
    user_id: UUID, pending_post_id: UUID, approved_post_id: UUID
) -> Optional[UserEventResponse]:
    """
    Create a user event that tracks the relationship between a pending post and its
    approved version.

    Args:
        user_id: UUID of the user who approved the post
        pending_post_id: UUID of the pending post that was approved
        approved_post_id: UUID of the new approved post

    Returns:
        UserEventSchema if created successfully, None otherwise
    """
    try:
        # Create metadata with both IDs to enable lookups in either direction
        metadata: Dict[str, Any] = {
            "pending_post_id": str(pending_post_id),
            "approved_post_id": str(approved_post_id),
        }

        # Create the event - this already returns a UserEventResponse
        event = await create_event(
            event_type="post_approval",
            user_id=user_id,
            resource_type="post",
            resource_id=approved_post_id,
            metadata=metadata,
        )

        logger.info(
            f"Created post approval event linking pending post {pending_post_id} "
            f"to approved post {approved_post_id}"
        )

        return event

    except Exception as e:
        logger.error(
            f"Failed to create post approval event for pending post "
            f"{pending_post_id}: {e}"
        )
        return None
