from typing import Optional
from uuid import UUID

from backend.converters.rejected_post_to_schema import rejected_post_to_schema
from backend.db.models.rejected_post import RejectedPost
from backend.schemas.rejected_post import RejectedPostResponse


async def get_rejected_post_by_id(
    rejected_post_id: UUID,
) -> Optional[RejectedPostResponse]:
    """
    Get a rejected post by ID.

    Args:
        rejected_post_id: ID of the rejected post to retrieve

    Returns:
        RejectedPostResponse: The rejected post if found, None otherwise
    """
    rejected_post = await RejectedPost.get_or_none(id=rejected_post_id)

    if not rejected_post:
        return None

    return await rejected_post_to_schema(rejected_post)
