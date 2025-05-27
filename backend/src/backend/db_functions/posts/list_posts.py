# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import post_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse


async def list_posts(
    skip: int = 0,
    limit: int = 20,
    topic_id: Optional[UUID] = None,
    author_id: Optional[UUID] = None,
) -> PostList:
    """
    List posts with pagination and optional filters.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        topic_id: Optional filter by topic ID
        author_id: Optional filter by author ID

    Returns:
        PostList containing the posts and total count
    """
    # Build query with filters
    query = Post.all()

    if topic_id:
        query = query.filter(topic_id=topic_id)

    if author_id:
        query = query.filter(author_id=author_id)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    posts = await query.offset(skip).limit(limit)

    # Convert ORM models to schema objects using async converter
    post_responses: list[PostResponse] = []
    for post in posts:
        post_responses.append(await post_to_schema(post))

    return PostList(posts=post_responses, count=count)
