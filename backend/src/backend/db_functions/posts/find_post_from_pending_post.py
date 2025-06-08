"""
Find an approved post that was created from a pending post.
"""

import logging
from typing import Optional
from uuid import UUID

from backend.db.models.pending_post import PendingPost
from backend.db_functions.posts.get_post_by_id import get_post_by_id
from backend.db_functions.user_events.get_post_approval_event import (
    get_post_approval_event,
)
from backend.schemas.post import PostResponse

logger = logging.getLogger(__name__)


async def find_post_from_pending_post(pending_post_id: UUID) -> Optional[PostResponse]:
    """
    Find an approved post that was created from a pending post.

    Since there's no direct reference between pending posts and approved posts,
    this function checks if the pending post still exists.

    Args:
        pending_post_id: UUID of the pending post to find the approved version for

    Returns:
        PostResponse schema of the approved post if found, None otherwise
    """
    try:
        # First, check if the pending post still exists
        pending_post = await PendingPost.get_or_none(id=pending_post_id)

        if pending_post:
            # Pending post still exists, so it hasn't been approved yet
            logger.debug(
                f"Pending post {pending_post_id} still exists, not approved yet"
            )
            return None

        # Pending post doesn't exist, which might mean it was approved
        # Try to find the approval event that links the pending post to an approved post
        approval_event = await get_post_approval_event(pending_post_id)

        if approval_event and approval_event.metadata:
            # Extract the approved post ID from the event metadata
            approved_post_id_str = approval_event.metadata.get("approved_post_id")

            if approved_post_id_str:
                try:
                    # Convert string ID to UUID and fetch the approved post
                    approved_post_id = UUID(approved_post_id_str)
                    approved_post = await get_post_by_id(approved_post_id)

                    if approved_post:
                        logger.info(
                            f"Found approved post {approved_post_id} for "
                            f"pending post {pending_post_id} via event tracking"
                        )
                        return approved_post
                except ValueError as e:
                    logger.error(f"Invalid UUID in approval event metadata: {e}")

        # If we get here, either no approval event was found or the approved post
        # couldn't be retrieved
        logger.debug(f"No approval event found for pending post {pending_post_id}")
        return None

    except Exception as e:
        logger.error(
            f"Error finding approved post for pending post {pending_post_id}: {e}"
        )
        return None
