from typing import Optional
from uuid import UUID

from backend.converters.pending_post_to_schema import pending_post_to_schema
from backend.db.models.pending_post import PendingPost
from backend.schemas.pending_post import PendingPostResponse


async def get_pending_post_by_id(
    pending_post_id: UUID,
) -> Optional[PendingPostResponse]:
    pending_post = await PendingPost.get_or_none(id=pending_post_id)
    if not pending_post:
        return None

    return await pending_post_to_schema(pending_post)
