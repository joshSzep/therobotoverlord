# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from tortoise.exceptions import DoesNotExist

# Project-specific imports
from backend.db.models.topic import Topic
from backend.db.models.user import User
from backend.utils.auth import get_current_user

router = APIRouter()


@router.delete("/{topic_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        topic = await Topic.get(id=topic_id).prefetch_related("author")
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Check if the current user is the author
    if str(topic.author.id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this topic",
        )

    # Delete the topic (this will also delete related topic_tags due to cascading)
    await topic.delete()
