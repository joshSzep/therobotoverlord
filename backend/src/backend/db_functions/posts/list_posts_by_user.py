# Standard library imports
from typing import List
from typing import Union
import uuid

from backend.converters.post_to_schema import post_to_schema

# Project-specific imports
from backend.db.models.post import Post
from backend.schemas.post import PostResponse


async def list_posts_by_user(
    user_id: uuid.UUID,
    limit: int = 10,
    offset: int = 0,
    count_only: bool = False,
) -> Union[List[PostResponse], int]:
    """
    List posts created by a specific user with pagination.

    Args:
        user_id: The ID of the user whose posts to retrieve
        limit: Maximum number of posts to return
        offset: Number of posts to skip for pagination
        count_only: If True, only return the count of posts

    Returns:
        Either a list of PostResponse objects or the count of posts
    """
    # Base query for posts by this user
    base_query = Post.filter(author_id=user_id)

    # If we only need the count, return it
    if count_only:
        return await base_query.count()

    # Get posts with pagination
    posts = await base_query.order_by("-created_at").offset(offset).limit(limit).all()

    # Convert to schema objects
    return [await post_to_schema(post) for post in posts]
