# Standard library imports
import logging
from typing import List
import uuid

# Project-specific imports
from backend.converters.pending_post_to_schema import pending_post_to_schema
from backend.db.models.pending_post import PendingPost
from backend.schemas.pending_post import PendingPostResponse

# Set up logger
logger = logging.getLogger(__name__)


async def list_pending_posts_by_user(
    user_id: uuid.UUID,
    limit: int = 10,
    offset: int = 0,
) -> List[PendingPostResponse]:
    """
    List pending posts created by a specific user with pagination.

    Args:
        user_id: The ID of the user whose pending posts to retrieve
        limit: Maximum number of posts to return
        offset: Number of posts to skip for pagination

    Returns:
        A list of PostResponse objects for pending posts
    """
    # Log the query parameters
    logger.debug(
        "Fetching pending posts for user_id:"
        f" {user_id}, limit: {limit}, offset: {offset}"
    )

    # Get allowed fields for debugging
    model_fields = [field for field in dir(PendingPost) if not field.startswith("_")]
    logger.debug(f"Available PendingPost model fields: {model_fields[:50]}...")

    # Query for pending posts by this user - using author_id instead of user_id
    try:
        # Filter by author_id to get pending posts for this user
        pending_posts = (
            await PendingPost.filter(author_id=user_id)
            .order_by("-created_at")
            .offset(offset)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(pending_posts)} pending posts for user {user_id}")
    except Exception as e:
        logger.error(f"Error fetching pending posts: {str(e)}")
        # Return empty list on error
        return []

    # Convert to schema objects
    return [await pending_post_to_schema(post) for post in pending_posts]
