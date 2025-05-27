# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.converters import topic_to_schema
from backend.db.models.topic import Topic
from backend.schemas.topic import TopicResponse


async def create_topic(
    title: str,
    description: str,
    created_by_id: UUID,
) -> TopicResponse:
    topic = await Topic.create(
        title=title,
        description=description,
        author_id=created_by_id,
    )
    return await topic_to_schema(topic)
