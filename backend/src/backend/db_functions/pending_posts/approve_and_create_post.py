import logging
from typing import Optional
from uuid import UUID

from backend.db.models.pending_post import PendingPost
from backend.db.models.post import Post
from backend.db_functions.posts.get_post_by_id import get_post_by_id
from backend.db_functions.user_events.create_post_approval_event import (
    create_post_approval_event,
)
from backend.db_functions.user_stats.increment_user_approval_count import (
    increment_user_approval_count,
)
from backend.schemas.post import PostResponse

logger = logging.getLogger(__name__)


async def approve_and_create_post(pending_post_id: UUID) -> Optional[PostResponse]:
    """
    Approves a pending post and creates a regular post from it.
    Deletes the pending post after creating the regular post.

    Also creates a user event to track the relationship between the pending post
    and the approved post for future reference.
    """
    pending_post = await PendingPost.get_or_none(id=pending_post_id)
    if not pending_post:
        logger.warning(f"Cannot approve pending post {pending_post_id}: not found")
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

    logger.info(f"Created approved post {post.id} from pending post {pending_post_id}")

    # Update user stats for post approval
    await increment_user_approval_count(author.id, post.id)

    # Create a post approval event to track the relationship
    # This will allow us to find the approved post from the pending post ID later
    event = await create_post_approval_event(
        user_id=author.id, pending_post_id=pending_post_id, approved_post_id=post.id
    )

    if not event:
        logger.warning(
            f"Failed to create post approval event for pending post {pending_post_id}"
        )

    # Delete the pending post
    await pending_post.delete()

    # Return the newly created post as a schema
    result = await get_post_by_id(post.id)
    return result
