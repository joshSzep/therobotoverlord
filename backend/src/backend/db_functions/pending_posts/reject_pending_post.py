from typing import Optional
from uuid import UUID

from backend.converters.rejected_post_to_schema import rejected_post_to_schema
from backend.db.models.pending_post import PendingPost
from backend.db.models.rejected_post import RejectedPost
from backend.schemas.rejected_post import RejectedPostResponse


async def reject_pending_post(
    pending_post_id: UUID, moderation_reason: str
) -> Optional[RejectedPostResponse]:
    """
    Rejects a pending post by creating a RejectedPost entry and deleting the
    PendingPost.
    """
    pending_post = await PendingPost.get_or_none(id=pending_post_id)
    if not pending_post:
        return None

    # Get related objects before we delete the pending post
    author = await pending_post.author
    topic = await pending_post.topic

    # Create the rejected post
    rejected_post = await RejectedPost.create(
        content=pending_post.content,
        author=author,
        topic=topic,
        parent_post_id=pending_post.parent_post_id,
        moderation_reason=moderation_reason,
    )

    # Delete the pending post
    await pending_post.delete()

    # Return the newly created rejected post as a schema
    result = await rejected_post_to_schema(rejected_post)
    return result
