# Standard library imports
from typing import List
from typing import Optional
from typing import Tuple
from uuid import UUID

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.db.models.topic_tag import TopicTag


class TopicTagRepository:
    @staticmethod
    async def get_topic_tag(topic_id: UUID, tag_id: UUID) -> Optional[TopicTag]:
        return await TopicTag.get_or_none(topic_id=topic_id, tag_id=tag_id)

    @staticmethod
    async def create_topic_tag(topic_id: UUID, tag_id: UUID) -> TopicTag:
        return await TopicTag.create(topic_id=topic_id, tag_id=tag_id)

    @staticmethod
    async def delete_topic_tag(topic_id: UUID, tag_id: UUID) -> bool:
        topic_tag = await TopicTag.get_or_none(topic_id=topic_id, tag_id=tag_id)
        if topic_tag:
            await topic_tag.delete()
            return True
        return False

    @staticmethod
    async def get_tags_for_topic(topic_id: UUID) -> List[Tag]:
        topic_tags = await TopicTag.filter(topic_id=topic_id).prefetch_related("tag")
        return [tt.tag for tt in topic_tags]

    @staticmethod
    async def get_topics_for_tag(tag_id: UUID) -> List[Topic]:
        topic_tags = await TopicTag.filter(tag_id=tag_id).prefetch_related("topic")
        return [tt.topic for tt in topic_tags]

    @staticmethod
    async def add_tags_to_topic(topic_id: UUID, tag_ids: List[UUID]) -> List[TopicTag]:
        topic_tags = []
        for tag_id in tag_ids:
            # Check if the relationship already exists
            existing = await TopicTag.get_or_none(topic_id=topic_id, tag_id=tag_id)
            if not existing:
                topic_tag = await TopicTag.create(topic_id=topic_id, tag_id=tag_id)
                topic_tags.append(topic_tag)
        return topic_tags

    @staticmethod
    async def remove_tags_from_topic(topic_id: UUID, tag_ids: List[UUID]) -> int:
        deleted_count = await TopicTag.filter(
            topic_id=topic_id, tag__id__in=tag_ids
        ).delete()
        return deleted_count

    @staticmethod
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
        tag_ids_to_add = [
            tag_id for tag_id in tag_ids if tag_id not in existing_tag_ids
        ]
        tag_ids_to_remove = [
            tag_id for tag_id in existing_tag_ids if tag_id not in tag_ids
        ]

        # Add new tags
        new_topic_tags = await TopicTagRepository.add_tags_to_topic(
            topic_id, tag_ids_to_add
        )

        # Remove tags that are no longer needed
        removed_count = 0
        if tag_ids_to_remove:
            removed_count = await TopicTagRepository.remove_tags_from_topic(
                topic_id, tag_ids_to_remove
            )

        return new_topic_tags, removed_count
