# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.db.models.topic_tag import TopicTag


async def get_topic_tag(topic_id: UUID, tag_id: UUID) -> Optional[TopicTag]:
    return await TopicTag.get_or_none(topic_id=topic_id, tag_id=tag_id)
