# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db_functions.topics import get_topic_by_id
from backend.schemas.topic import TopicResponse

router = APIRouter()


@router.get("/{topic_id}/", response_model=TopicResponse)
async def get_topic(topic_id: UUID) -> TopicResponse:
    # Get the topic using data access function
    topic = await get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # The repository already handles fetching related data and converting to schema
    return topic
