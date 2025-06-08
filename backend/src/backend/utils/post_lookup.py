"""
Post lookup utilities for finding posts regardless of their status.
"""

from typing import Optional
from typing import Union
from uuid import UUID

from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.db_functions.posts.get_post_by_id import get_post_by_id
from backend.db_functions.rejected_posts.get_rejected_post_by_id import (
    get_rejected_post_by_id,
)
from backend.schemas.pending_post import PendingPostResponse
from backend.schemas.post import PostResponse
from backend.schemas.post_lookup import PostLookupResult
from backend.schemas.post_lookup import PostType
from backend.schemas.rejected_post import RejectedPostResponse


async def find_post_by_id(
    post_id: UUID, current_user_id: Optional[UUID] = None
) -> Optional[
    Union[
        PostLookupResult[PostResponse],
        PostLookupResult[PendingPostResponse],
        PostLookupResult[RejectedPostResponse],
    ]
]:
    """
    Find any post by ID, regardless of its status or nesting level.

    Args:
        post_id: The UUID of the post to find
        current_user_id: Optional current user ID to check permissions

    Returns:
        PostLookupResult with post type and data, or None if not found or not accessible
    """
    # Check approved posts first
    post = await get_post_by_id(post_id)
    if post:
        return PostLookupResult(type=PostType.APPROVED, post=post, visible_to_user=True)

    # Check pending posts
    pending_post = await get_pending_post_by_id(post_id)
    if pending_post:
        # Check if user has permission to see this pending post
        visible_to_user = current_user_id and str(pending_post.author.id) == str(
            current_user_id
        )
        if visible_to_user:
            return PostLookupResult(
                type=PostType.PENDING, post=pending_post, visible_to_user=True
            )
        return PostLookupResult(
            type=PostType.PENDING, post=pending_post, visible_to_user=False
        )

    # Check rejected posts
    rejected_post = await get_rejected_post_by_id(post_id)
    if rejected_post:
        visible_to_user = current_user_id and str(rejected_post.author.id) == str(
            current_user_id
        )
        if visible_to_user:
            return PostLookupResult(
                type=PostType.REJECTED, post=rejected_post, visible_to_user=True
            )
        return PostLookupResult(
            type=PostType.REJECTED, post=rejected_post, visible_to_user=False
        )

    return None
