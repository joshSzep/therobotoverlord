# Standard library imports
from typing import List
from uuid import UUID

# Project-specific imports
from backend.db.models.topic_tag import TopicTag


async def add_tags_to_topic(topic_id: UUID, tag_ids: List[UUID]) -> List[TopicTag]:
    topic_tags = []
    for tag_id in tag_ids:
        # Check if the relationship already exists
        existing = await TopicTag.get_or_none(topic_id=topic_id, tag_id=tag_id)
        if not existing:
            topic_tag = await TopicTag.create(topic_id=topic_id, tag_id=tag_id)
            topic_tags.append(topic_tag)
    return topic_tags
