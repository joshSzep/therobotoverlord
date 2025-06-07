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
from backend.utils.admin_auth import get_admin_user

router = APIRouter()


@router.delete("/{topic_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: UUID,
    # This ensures only admins can delete topics
    current_user: User = Depends(get_admin_user),
) -> None:
    # Check if topic exists
    topic = await get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # No need to check if user is author - admin can delete any topic

    # Delete the topic (this will also delete related topic_tags due to cascading)
    success = await db_delete_topic(topic_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete topic",
        )
