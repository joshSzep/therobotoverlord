# Standard library imports
import logging
from typing import List
from uuid import UUID

# Project-specific imports
from backend.converters.pending_post_to_schema import pending_post_to_schema
from backend.db.models.pending_post import PendingPost
from backend.schemas.pending_post import PendingPostResponse

# Set up logger
logger = logging.getLogger(__name__)


async def list_pending_posts_by_topic_and_user(
    topic_id: UUID,
    user_id: UUID,
) -> List[PendingPostResponse]:
    """
    List pending posts for a specific topic created by a specific user.

    Args:
        topic_id: The ID of the topic to fetch pending posts for
        user_id: The ID of the user whose pending posts to retrieve

    Returns:
        A list of PendingPostResponse objects
    """
    # Log the query parameters
    logger.debug(f"Fetching pending posts for topic_id: {topic_id}, user_id: {user_id}")

    try:
        # Filter by topic_id and author_id to get pending posts for this topic by this
        # user
        pending_posts = (
            await PendingPost.filter(topic_id=topic_id, author_id=user_id)
            .order_by("-created_at")
            .all()
        )
        logger.debug(
            f"Found {len(pending_posts)} pending posts"
            f" for topic {topic_id} by user {user_id}"
        )
    except Exception as e:
        logger.error(f"Error fetching pending posts: {str(e)}")
        # Return empty list on error
        return []

    # Convert to schema objects
    return [await pending_post_to_schema(post) for post in pending_posts]
