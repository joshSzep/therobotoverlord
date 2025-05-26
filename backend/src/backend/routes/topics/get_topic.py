# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from tortoise.exceptions import DoesNotExist

# Project-specific imports
from backend.db.models.topic import Topic
from backend.routes.topics.schemas import TagResponse
from backend.routes.topics.schemas import TopicResponse

router = APIRouter()


@router.get("/{topic_id}/", response_model=TopicResponse)
async def get_topic(topic_id: UUID) -> TopicResponse:
    try:
        topic = await Topic.get(id=topic_id).prefetch_related(
            "author", "topic_tags__tag"
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Extract tags from the topic_tags relation
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

    return topic_response
