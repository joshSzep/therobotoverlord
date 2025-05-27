# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import topic_to_schema
from backend.db.models.topic import Topic
from backend.schemas.topic import TopicResponse


async def get_topic_by_id(topic_id: UUID) -> Optional[TopicResponse]:
    topic = await Topic.get_or_none(id=topic_id)
    if topic:
        return await topic_to_schema(topic)
    return None
