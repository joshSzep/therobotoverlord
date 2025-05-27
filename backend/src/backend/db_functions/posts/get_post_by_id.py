# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import post_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostResponse


async def get_post_by_id(post_id: UUID) -> Optional[PostResponse]:
    """
    Get a post by its ID.

    Args:
        post_id: The UUID of the post to retrieve

    Returns:
        PostResponse if found, None otherwise
    """
    post = await Post.get_or_none(id=post_id)
    if post:
        return await post_to_schema(post)
    return None
