# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.db.models.topic import Topic


async def delete_topic(topic_id: UUID) -> bool:
    topic = await Topic.get_or_none(id=topic_id)
    if topic:
        await topic.delete()
        return True
    return False
