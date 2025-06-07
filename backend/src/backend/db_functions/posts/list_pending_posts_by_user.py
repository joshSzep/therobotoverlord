# Standard library imports
from typing import List
import uuid

from backend.converters.post_to_schema import post_to_schema

# Project-specific imports
from backend.db.models.post import Post
from backend.schemas.post import PostResponse


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
    # Query for pending posts by this user
    posts = (
        await Post.filter(user_id=user_id, is_approved=False, is_rejected=False)
        .order_by("-created_at")
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Convert to schema objects
    return [await post_to_schema(post) for post in posts]
