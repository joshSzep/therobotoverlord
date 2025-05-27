# Standard library imports
from typing import List
from uuid import UUID

# Project-specific imports
from backend.converters import topic_to_schema
from backend.db.models.topic_tag import TopicTag
from backend.schemas.topic import TopicResponse


async def get_topics_for_tag(tag_id: UUID) -> List[TopicResponse]:
    topic_tags = await TopicTag.filter(tag_id=tag_id).prefetch_related("topic")
    topic_responses = []
    for tt in topic_tags:
        topic_responses.append(await topic_to_schema(tt.topic))
    return topic_responses
