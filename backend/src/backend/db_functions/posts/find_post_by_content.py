"""
Find a post by its content.
"""

import logging
from typing import Optional
from uuid import UUID

from backend.converters.post_to_schema import post_to_schema
from backend.db.models.pending_post import PendingPost
from backend.db.models.post import Post
from backend.schemas.post import PostResponse

# Set up logging
logger = logging.getLogger(__name__)


async def find_post_by_content(
    content: str,
    topic_id: UUID,
    author_id: UUID,
) -> Optional[PostResponse]:
    """
    Find an approved post by matching its content, topic, and author.

    This is used to find a post that was created from a pending post
    when we don't have a direct reference between them.

    Args:
        content: The content to match
        topic_id: The topic ID to match
        author_id: The author ID to match

    Returns:
        The matching PostResponse object or None if not found
    """
    logger.debug(f"Looking for post with content matching: {content[:50]}...")

    try:
        # Find the post with matching content, topic, and author
        post = await Post.filter(
            content=content, topic_id=topic_id, author_id=author_id
        ).first()

        if post:
            logger.debug(f"Found matching post with ID: {post.id}")
            return await post_to_schema(post)
        else:
            logger.debug("No matching post found")
            return None
    except Exception as e:
        logger.error(f"Error finding post by content: {str(e)}")
        return None


async def find_approved_version_of_pending_post(
    pending_post_id: UUID,
) -> Optional[PostResponse]:
    """
    Find the approved version of a pending post that has been approved.

    This function tries to find a post that was created from a pending post
    by matching the content, topic, and author.

    Args:
        pending_post_id: The ID of the pending post to find the approved version of

    Returns:
        The matching PostResponse object or None if not found
    """
    logger.debug(f"Looking for approved version of pending post: {pending_post_id}")

    try:
        # Try to get the pending post first
        pending_post = await PendingPost.get_or_none(id=pending_post_id)

        # If pending post still exists, it hasn't been approved yet
        if pending_post:
            logger.debug(
                f"Pending post {pending_post_id} still exists, not approved yet"
            )
            return None

        # If we can't find the pending post, it might have been approved and deleted
        # We need to check the user events or try to find a matching post

        # For now, we'll return None as we need more context to find the approved post
        # In a real implementation, we would check user events or other tracking
        # mechanisms
        logger.debug(
            f"Pending post {pending_post_id} not found, "
            f"but we can't determine the approved version"
        )
        return None

    except Exception as e:
        logger.error(f"Error finding approved version of pending post: {str(e)}")
        return None
