# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.converters import post_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse


async def list_post_replies(post_id: UUID, skip: int = 0, limit: int = 20) -> PostList:
    """
    List replies to a specific post with pagination.

    Args:
        post_id: The UUID of the parent post
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return

    Returns:
        PostList containing the reply posts and total count
    """
    query = Post.filter(parent_post_id=post_id)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    replies = await query.offset(skip).limit(limit)

    # Convert ORM models to schema objects using async converter
    reply_responses: list[PostResponse] = []
    for reply in replies:
        reply_responses.append(await post_to_schema(reply))

    return PostList(posts=reply_responses, count=count)
