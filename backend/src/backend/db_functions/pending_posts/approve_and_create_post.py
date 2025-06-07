from typing import Optional
from uuid import UUID

from backend.db.models.pending_post import PendingPost
from backend.db.models.post import Post
from backend.db_functions.posts.get_post_by_id import get_post_by_id
from backend.db_functions.user_stats.increment_user_approval_count import (
    increment_user_approval_count,
)
from backend.schemas.post import PostResponse


async def approve_and_create_post(pending_post_id: UUID) -> Optional[PostResponse]:
    """
    Approves a pending post and creates a regular post from it.
    Deletes the pending post after creating the regular post.
    """
    pending_post = await PendingPost.get_or_none(id=pending_post_id)
    if not pending_post:
        return None

    # Get related objects before we delete the pending post
    author = await pending_post.author
    topic = await pending_post.topic

    # Create the regular post
    post = await Post.create(
        content=pending_post.content,
        author=author,
        topic=topic,
        parent_post_id=pending_post.parent_post_id,
    )

    # Update user stats for post approval
    await increment_user_approval_count(author.id, post.id)

    # Delete the pending post
    await pending_post.delete()

    # Return the newly created post as a schema
    result = await get_post_by_id(post.id)
    return result
