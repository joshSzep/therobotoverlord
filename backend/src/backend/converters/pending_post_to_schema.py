from backend.converters.user_to_schema import user_to_schema
from backend.db.models.pending_post import PendingPost
from backend.schemas.pending_post import PendingPostResponse


async def pending_post_to_schema(pending_post: PendingPost) -> PendingPostResponse:
    author = await pending_post.author
    topic = await pending_post.topic

    return PendingPostResponse(
        id=pending_post.id,
        content=pending_post.content,
        author=await user_to_schema(author),
        topic_id=topic.id,
        parent_post_id=pending_post.parent_post_id,
        created_at=pending_post.created_at,
        updated_at=pending_post.updated_at,
    )
