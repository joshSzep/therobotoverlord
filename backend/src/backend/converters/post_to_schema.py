from backend.converters.user_to_schema import user_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostResponse


async def post_to_schema(post: Post) -> PostResponse:
    # Fetch related data
    await post.fetch_related("author", "topic")
    await post.fetch_related("parent_post")

    # Calculate reply count
    reply_count = await Post.filter(parent_post_id=post.id).count()

    # Get topic_id safely - it should never be None for a valid post
    if not hasattr(post, "topic") or not post.topic:
        raise ValueError(f"Post {post.id} has no associated topic")
    topic_id = post.topic.id

    # Get parent_post_id safely
    parent_id = None
    if hasattr(post, "parent_post") and post.parent_post:
        parent_id = post.parent_post.id

    return PostResponse(
        id=post.id,
        content=post.content,
        author=await user_to_schema(post.author),
        topic_id=topic_id,
        parent_post_id=parent_id,
        created_at=post.created_at,
        updated_at=post.updated_at,
        reply_count=reply_count,
    )
