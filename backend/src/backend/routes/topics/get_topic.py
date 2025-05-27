# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.repositories.topic_repository import TopicRepository
from backend.repositories.topic_tag_repository import TopicTagRepository
from backend.routes.topics.schemas import TagResponse
from backend.routes.topics.schemas import TopicResponse

router = APIRouter()


@router.get("/{topic_id}/", response_model=TopicResponse)
async def get_topic(topic_id: UUID) -> TopicResponse:
    # Get the topic
    topic = await TopicRepository.get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Fetch related author
    await topic.fetch_related("author")

    # Get tags for this topic
    topic_tags = await TopicTagRepository.get_tags_for_topic(topic.id)
    tags = [
        TagResponse(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
        )
        for tag in topic_tags
    ]

    # Create the response object
    topic_response = TopicResponse.model_validate(topic)
    topic_response.tags = tags

    return topic_response
