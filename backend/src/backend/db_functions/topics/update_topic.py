# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import topic_to_schema
from backend.db.models.topic import Topic
from backend.schemas.topic import TopicResponse


async def update_topic(
    topic_id: UUID, title: Optional[str] = None, description: Optional[str] = None
) -> Optional[TopicResponse]:
    topic = await Topic.get_or_none(id=topic_id)
    if topic:
        if title is not None:
            topic.title = title
        if description is not None:
            topic.description = description
        await topic.save()
        return await topic_to_schema(topic)
    return None
