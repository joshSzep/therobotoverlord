# Standard library imports

# Project-specific imports
from backend.converters import topic_to_schema
from backend.db.models.topic import Topic
from backend.schemas.topic import TopicList
from backend.schemas.topic import TopicResponse


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
