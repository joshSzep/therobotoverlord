# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.db.models.topic_tag import TopicTag


async def delete_topic_tag(topic_id: UUID, tag_id: UUID) -> bool:
    topic_tag = await TopicTag.get_or_none(topic_id=topic_id, tag_id=tag_id)
    if topic_tag:
        await topic_tag.delete()
        return True
    return False
