# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.converters import post_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse


async def list_posts_by_topic(
    topic_id: UUID, skip: int = 0, limit: int = 20
) -> PostList:
    # Query posts that belong to the specified topic and are not replies
    query = Post.filter(topic_id=topic_id, parent_post_id=None)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    posts = await query.offset(skip).limit(limit).order_by("-created_at")

    # Convert ORM models to schema objects
    post_responses: list[PostResponse] = []
    for post in posts:
        post_responses.append(await post_to_schema(post))

    return PostList(posts=post_responses, count=count)
