# Standard library imports
from typing import List
from typing import Tuple
from uuid import UUID

# Project-specific imports
from backend.db.models.topic_tag import TopicTag
from backend.db_functions.topic_tags.add_tags_to_topic import add_tags_to_topic
from backend.db_functions.topic_tags.remove_tags_from_topic import (
    remove_tags_from_topic,
)


async def set_topic_tags(
    topic_id: UUID, tag_ids: List[UUID]
) -> Tuple[List[TopicTag], int]:
    # Get existing tag IDs for this topic
    # Access tag.id instead of tag_id since it's a ForeignKey relationship
    existing_tag_ids = [
        tt.tag.id
        for tt in await TopicTag.filter(topic_id=topic_id).prefetch_related("tag")
    ]

    # Determine which tags to add and which to remove
    tag_ids_to_add = [tag_id for tag_id in tag_ids if tag_id not in existing_tag_ids]
    tag_ids_to_remove = [tag_id for tag_id in existing_tag_ids if tag_id not in tag_ids]

    # Add new tags
    new_topic_tags = await add_tags_to_topic(topic_id, tag_ids_to_add)

    # Remove tags that are no longer needed
    removed_count = 0
    if tag_ids_to_remove:
        removed_count = await remove_tags_from_topic(topic_id, tag_ids_to_remove)

    return new_topic_tags, removed_count
