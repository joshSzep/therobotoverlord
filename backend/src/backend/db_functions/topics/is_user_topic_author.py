# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.db.models.topic import Topic


async def is_user_topic_author(topic_id: UUID, user_id: UUID) -> bool:
    topic = await Topic.get_or_none(id=topic_id)
    if not topic:
        return False

    await topic.fetch_related("author")
    return str(topic.author.id) == str(user_id)
