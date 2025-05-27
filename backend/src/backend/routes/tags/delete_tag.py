# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db.models.user import User
from backend.db_functions.tags import delete_tag as db_delete_tag
from backend.db_functions.tags import get_tag_by_id
from backend.db_functions.topic_tags import get_topics_for_tag
from backend.utils.auth import get_current_user

router = APIRouter()


@router.delete("/{tag_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    # Only allow admins to delete tags
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete tags",
        )

    # Get the tag - function expects UUID objects
    tag = await get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    # Check if the tag is used by any topics
    topics = await get_topics_for_tag(tag_id)
    if topics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete tag as it is used by {len(topics)} topics",
        )

    # Delete the tag - function expects UUID objects
    success = await db_delete_tag(tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tag",
        )
