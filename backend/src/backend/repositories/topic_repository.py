# Standard library imports
from typing import List
from typing import Optional
from typing import Tuple
from uuid import UUID

# Project-specific imports
from backend.db.models.topic import Topic


class TopicRepository:
    @staticmethod
    async def get_topic_by_id(topic_id: UUID) -> Optional[Topic]:
        return await Topic.get_or_none(id=topic_id)

    @staticmethod
    async def list_topics(
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Topic], int]:
        query = Topic.all()
        count = await query.count()
        topics = await query.offset(skip).limit(limit)
        return topics, count

    @staticmethod
    async def create_topic(
        title: str,
        description: str,
        created_by_id: UUID,
    ) -> Topic:
        return await Topic.create(
            title=title,
            description=description,
            author_id=created_by_id,
        )

    @staticmethod
    async def update_topic(
        topic_id: UUID, title: Optional[str] = None, description: Optional[str] = None
    ) -> Optional[Topic]:
        topic = await Topic.get_or_none(id=topic_id)
        if topic:
            if title is not None:
                topic.title = title
            if description is not None:
                topic.description = description
            await topic.save()
        return topic

    @staticmethod
    async def delete_topic(topic_id: UUID) -> bool:
        topic = await Topic.get_or_none(id=topic_id)
        if topic:
            await topic.delete()
            return True
        return False
