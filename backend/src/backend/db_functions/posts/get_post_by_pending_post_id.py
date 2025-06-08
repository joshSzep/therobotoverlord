"""
Get an approved post by its original pending post ID.
"""

import logging
from typing import Optional
from uuid import UUID

from backend.converters.post_to_schema import post_to_schema
from backend.db.models.post import Post
from backend.db_functions.user_events.get_post_approval_event import (
    get_post_approval_event,
)
from backend.schemas.post import PostResponse

# Set up logging
logger = logging.getLogger(__name__)


async def get_post_by_pending_post_id(
    pending_post_id: UUID,
) -> Optional[PostResponse]:
    """
    Get an approved post that was created from a pending post.

    This function uses the user_events system to find the relationship between
    a pending post and its approved version.

    Args:
        pending_post_id: The ID of the original pending post

    Returns:
        The approved PostResponse object or None if not found
    """
    # Log the query parameters
    logger.debug(f"Looking for approved post from pending post ID: {pending_post_id}")

    try:
        # First check if we have an event tracking this approval
        event = await get_post_approval_event(pending_post_id)

        if event and event.metadata and "approved_post_id" in event.metadata:
            # Extract the approved post ID from the event metadata
            approved_post_id = UUID(event.metadata["approved_post_id"])
            logger.debug(
                f"Found approval event linking pending post {pending_post_id} "
                f"to approved post {approved_post_id}"
            )

            # Get the approved post
            post = await Post.get_or_none(id=approved_post_id)
            if post:
                return await post_to_schema(post)

        # If no event found or post not found, log and return None
        logger.debug(f"No approved post found for pending post {pending_post_id}")
        return None

    except Exception as e:
        logger.error(f"Error finding post by pending post ID: {e}")
        return None
