"""
List pending posts by topic ID.
"""

import logging
from typing import List
from uuid import UUID

from backend.converters.pending_post_to_schema import pending_post_to_schema
from backend.db.models.pending_post import PendingPost
from backend.schemas.pending_post import PendingPostResponse

# Set up logging
logger = logging.getLogger(__name__)


async def list_pending_posts_by_topic(
    topic_id: UUID,
) -> List[PendingPostResponse]:
    """
    List all pending posts for a specific topic.

    Args:
        topic_id: The ID of the topic to fetch pending posts for

    Returns:
        A list of PendingPostResponse objects
    """
    # Log the query parameters
    logger.debug(f"Fetching all pending posts for topic_id: {topic_id}")

    try:
        # Filter by topic_id to get all pending posts for this topic
        pending_posts = (
            await PendingPost.filter(topic_id=topic_id).order_by("-created_at").all()
        )
        logger.debug(f"Found {len(pending_posts)} pending posts for topic {topic_id}")
    except Exception as e:
        logger.error(f"Error fetching pending posts: {str(e)}")
        # Return empty list on error
        return []

    # Convert to schema objects
    return [await pending_post_to_schema(post) for post in pending_posts]
