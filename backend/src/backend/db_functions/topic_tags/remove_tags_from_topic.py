# Standard library imports
from typing import List
from uuid import UUID

# Project-specific imports
from backend.db.models.topic_tag import TopicTag


async def remove_tags_from_topic(topic_id: UUID, tag_ids: List[UUID]) -> int:
    deleted_count = await TopicTag.filter(
        topic_id=topic_id, tag__id__in=tag_ids
    ).delete()
    return deleted_count
