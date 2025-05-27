# Standard library imports
from typing import List
from uuid import UUID

# Project-specific imports
from backend.converters import tag_to_schema
from backend.db.models.topic_tag import TopicTag
from backend.schemas.tag import TagResponse


async def get_tags_for_topic(topic_id: UUID) -> List[TagResponse]:
    topic_tags = await TopicTag.filter(topic_id=topic_id).prefetch_related("tag")
    tag_responses = []
    for tt in topic_tags:
        tag_responses.append(await tag_to_schema(tt.tag))
    return tag_responses
