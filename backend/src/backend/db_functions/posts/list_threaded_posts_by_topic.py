# Standard library imports
import logging
from typing import Dict
from typing import List
from uuid import UUID

# Project-specific imports
from backend.converters import post_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse

# Set up logger
logger = logging.getLogger(__name__)


async def list_threaded_posts_by_topic(
    topic_id: UUID, skip: int = 0, limit: int = 20
) -> PostList:
    """
    List posts for a topic in a threaded structure with pagination.

    Args:
        topic_id: The ID of the topic to retrieve posts for
        skip: Number of top-level posts to skip for pagination
        limit: Maximum number of top-level posts to return

    Returns:
        A PostList containing top-level posts with their replies
    """
    # Query top-level posts (no parent) that belong to the specified topic
    query = Post.filter(topic_id=topic_id, parent_post=None)

    # Get total count of top-level posts for pagination
    count = await query.count()

    # Apply pagination to top-level posts
    top_level_posts = await query.offset(skip).limit(limit).order_by("-created_at")

    # Convert top-level posts to schema objects
    post_responses: List[PostResponse] = []
    post_id_map: Dict[UUID, PostResponse] = {}

    # First, process all top-level posts
    for post in top_level_posts:
        post_schema = await post_to_schema(post)
        post_responses.append(post_schema)
        post_id_map[post.id] = post_schema

    # Now fetch all replies for these posts
    if top_level_posts:
        top_level_ids = [post.id for post in top_level_posts]

        # Get all replies for the top-level posts
        all_replies = (
            await Post.filter(topic_id=topic_id)
            .filter(parent_post__id__in=top_level_ids)
            .order_by("created_at")
        )

        # Convert replies to schema objects and organize them
        for reply in all_replies:
            reply_schema = await post_to_schema(reply)

            # Find the parent post in our map
            if reply.parent_post and reply.parent_post.id in post_id_map:
                parent = post_id_map[reply.parent_post.id]

                # Initialize replies list if it doesn't exist
                if not hasattr(parent, "replies"):
                    parent.replies = []

                # Add this reply to the parent's replies
                parent.replies.append(reply_schema)

                # Add this reply to our map in case it has its own replies
                post_id_map[reply.id] = reply_schema

    logger.debug(f"Retrieved {len(post_responses)} threaded posts for topic {topic_id}")
    return PostList(posts=post_responses, count=count)
