# Standard library imports
from typing import Dict
from typing import List
from uuid import UUID

# Project-specific imports
from backend.db_functions.topics.get_topic_by_id import get_topic_by_id
from backend.schemas.post import PostResponse
from backend.schemas.topic import TopicResponse


async def enhance_posts_with_topics(
    posts: List[PostResponse],
) -> Dict[UUID, TopicResponse]:
    """
    Fetch topic information for a list of posts.

    Args:
        posts: List of PostResponse objects

    Returns:
        Dictionary mapping topic_id to TopicResponse
    """
    # Extract unique topic IDs from posts
    topic_ids = {post.topic_id for post in posts}

    # Fetch topic information for each unique topic ID
    topic_map: Dict[UUID, TopicResponse] = {}
    for topic_id in topic_ids:
        topic = await get_topic_by_id(topic_id)
        if topic:
            topic_map[topic_id] = topic

    return topic_map
