# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.db.models.topic_tag import TopicTag


async def create_topic_tag(topic_id: UUID, tag_id: UUID) -> TopicTag:
    return await TopicTag.create(topic_id=topic_id, tag_id=tag_id)
