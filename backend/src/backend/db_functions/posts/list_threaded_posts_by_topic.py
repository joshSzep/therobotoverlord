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

    # Now fetch ALL replies for the topic (not just direct replies to top-level posts)
    # This allows us to build the complete threading structure
    if top_level_posts:
        # Get all posts for this topic that are replies (have a parent)
        all_replies = (
            await Post.filter(topic_id=topic_id)
            .exclude(parent_post=None)
            .order_by("created_at")
        )

        # Convert all replies to schema objects
        reply_schemas = []
        for reply in all_replies:
            reply_schema = await post_to_schema(reply)
            reply_schemas.append(reply_schema)
            post_id_map[reply.id] = reply_schema

        # Now organize all replies into their proper parent-child relationships
        for reply in all_replies:
            reply_schema = post_id_map[reply.id]

            # If the parent is in our map (either a top-level post or another reply)
            if reply.parent_post and reply.parent_post.id in post_id_map:
                parent = post_id_map[reply.parent_post.id]

                # Initialize replies list if it doesn't exist
                if not hasattr(parent, "replies"):
                    parent.replies = []

                # Add this reply to the parent's replies
                parent.replies.append(reply_schema)

    logger.debug(f"Retrieved {len(post_responses)} threaded posts for topic {topic_id}")
    return PostList(posts=post_responses, count=count)
