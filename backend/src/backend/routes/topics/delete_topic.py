# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db.models.user import User  # Keep for type annotation
from backend.db_functions.topics import delete_topic as db_delete_topic
from backend.db_functions.topics import get_topic_by_id
from backend.db_functions.topics import is_user_topic_author
from backend.utils.auth import get_current_user

router = APIRouter()


@router.delete("/{topic_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    # Check if topic exists
    topic = await get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Check if the current user is the author
    is_author = await is_user_topic_author(topic_id, current_user.id)
    if not is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this topic",
        )

    # Delete the topic (this will also delete related topic_tags due to cascading)
    success = await db_delete_topic(topic_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete topic",
        )
