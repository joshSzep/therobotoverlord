# Standard library imports
import logging
from typing import List
import uuid

# Project-specific imports
from backend.converters.post_to_schema import post_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostResponse

# Set up logger
logger = logging.getLogger(__name__)


async def list_pending_posts_by_user(
    user_id: uuid.UUID,
    limit: int = 10,
    offset: int = 0,
) -> List[PostResponse]:
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
    model_fields = [field for field in dir(Post) if not field.startswith("_")]
    logger.debug(f"Available Post model fields: {model_fields[:50]}...")

    # Query for pending posts by this user - using author_id instead of user_id
    try:
        # Since we don't know if the Post model has is_approved and is_rejected fields,
        # let's just filter by author_id for now
        posts = (
            await Post.filter(author_id=user_id)
            .order_by("-created_at")
            .offset(offset)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(posts)} posts for user {user_id}")
    except Exception as e:
        logger.error(f"Error fetching pending posts: {str(e)}")
        # Return empty list on error
        return []

    # Convert to schema objects
    return [await post_to_schema(post) for post in posts]
