from uuid import UUID

from backend.converters.pending_post_to_schema import pending_post_to_schema
from backend.db.models.pending_post import PendingPost
from backend.schemas.pending_post import PendingPostCreate
from backend.schemas.pending_post import PendingPostResponse


async def create_pending_post(
    user_id: UUID,
    pending_post_data: PendingPostCreate,
) -> PendingPostResponse:
    pending_post = await PendingPost.create(
        author_id=user_id,
        topic_id=pending_post_data.topic_id,
        content=pending_post_data.content,
        parent_post_id=pending_post_data.parent_post_id,
    )

    return await pending_post_to_schema(pending_post)
