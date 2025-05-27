# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import topic_to_schema
from backend.db.models.topic import Topic
from backend.schemas.topic import TopicList
from backend.schemas.topic import TopicResponse


class TopicRepository:
    @staticmethod
    async def get_topic_by_id(topic_id: UUID) -> Optional[TopicResponse]:
        topic = await Topic.get_or_none(id=topic_id)
        if topic:
            return await topic_to_schema(topic)
        return None

    @staticmethod
    async def is_user_topic_author(topic_id: UUID, user_id: UUID) -> bool:
        topic = await Topic.get_or_none(id=topic_id)
        if not topic:
            return False

        await topic.fetch_related("author")
        return str(topic.author.id) == str(user_id)

    @staticmethod
    async def list_topics(
        skip: int = 0,
        limit: int = 20,
    ) -> TopicList:
        query = Topic.all()
        count = await query.count()
        topics = await query.offset(skip).limit(limit)

        # Convert ORM models to schema objects using async converter
        topic_responses: list[TopicResponse] = []
        for topic in topics:
            topic_responses.append(await topic_to_schema(topic))

        return TopicList(topics=topic_responses, count=count)

    @staticmethod
    async def create_topic(
        title: str,
        description: str,
        created_by_id: UUID,
    ) -> TopicResponse:
        topic = await Topic.create(
            title=title,
            description=description,
            author_id=created_by_id,
        )
        return await topic_to_schema(topic)

    @staticmethod
    async def update_topic(
        topic_id: UUID, title: Optional[str] = None, description: Optional[str] = None
    ) -> Optional[TopicResponse]:
        topic = await Topic.get_or_none(id=topic_id)
        if topic:
            if title is not None:
                topic.title = title
            if description is not None:
                topic.description = description
            await topic.save()
            return await topic_to_schema(topic)
        return None

    @staticmethod
    async def delete_topic(topic_id: UUID) -> bool:
        topic = await Topic.get_or_none(id=topic_id)
        if topic:
            await topic.delete()
            return True
        return False
