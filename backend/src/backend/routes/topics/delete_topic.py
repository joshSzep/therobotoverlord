# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db.models.user import User  # Keep for type annotation
from backend.repositories.topic_repository import TopicRepository
from backend.utils.auth import get_current_user

router = APIRouter()


@router.delete("/{topic_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    # Get the topic
    topic = await TopicRepository.get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Fetch related author
    await topic.fetch_related("author")

    # Check if the current user is the author
    if str(topic.author.id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this topic",
        )

    # Delete the topic (this will also delete related topic_tags due to cascading)
    success = await TopicRepository.delete_topic(topic_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete topic",
        )
