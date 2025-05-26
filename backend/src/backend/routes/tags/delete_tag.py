# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from tortoise.exceptions import DoesNotExist

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db.models.user import User
from backend.utils.auth import get_current_user

router = APIRouter()


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
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

    try:
        tag = await Tag.get(id=tag_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    # Check if the tag is used by any topics
    tag_count = await tag.topic_tags.all().count()
    if tag_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete tag as it is used by {tag_count} topics",
        )

    # Delete the tag
    await tag.delete()
