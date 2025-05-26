# Standard library imports
from typing import Optional

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.db.models.topic import Topic
from backend.routes.topics.schemas import TagResponse
from backend.routes.topics.schemas import TopicList
from backend.routes.topics.schemas import TopicResponse

router = APIRouter()


@router.get("/", response_model=TopicList)
async def list_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    tag: Optional[str] = None,
) -> TopicList:
    query = Topic.all().prefetch_related("author", "topic_tags__tag")

    if tag:
        # Filter by tag if provided
        query = query.filter(topic_tags__tag__slug=tag)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    topics = await query.offset(skip).limit(limit)

    # Convert to response model
    topic_responses: list[TopicResponse] = []
    for topic in topics:
        # Extract tags from the prefetched topic_tags relation
        tags = [
            TagResponse(
                id=tt.tag.id,
                name=tt.tag.name,
                slug=tt.tag.slug,
            )
            for tt in topic.topic_tags
        ]

        # Create the response object
        topic_response = TopicResponse.model_validate(topic)
        topic_response.tags = tags
        topic_responses.append(topic_response)

    return TopicList(topics=topic_responses, count=count)
