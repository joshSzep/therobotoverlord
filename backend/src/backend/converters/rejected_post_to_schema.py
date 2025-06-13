from backend.converters.user_to_schema import user_to_schema
from backend.db.models.rejected_post import RejectedPost
from backend.schemas.rejected_post import RejectedPostResponse


async def rejected_post_to_schema(rejected_post: RejectedPost) -> RejectedPostResponse:
    # Fetch related author and topic
    await rejected_post.fetch_related("author", "topic")

    return RejectedPostResponse(
        id=rejected_post.id,
        content=rejected_post.content,
        author=await user_to_schema(rejected_post.author),
        topic_id=rejected_post.topic.id,
        parent_post_id=rejected_post.parent_post_id,
        created_at=rejected_post.created_at,
        updated_at=rejected_post.updated_at,
        moderation_reason=rejected_post.moderation_reason,
    )
