# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from slugify import slugify
from tortoise.exceptions import DoesNotExist
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db.models.user import User
from backend.routes.tags.schemas import TagCreate
from backend.routes.tags.schemas import TagResponse
from backend.utils.auth import get_current_user

router = APIRouter()


@router.put("/{tag_id}/", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
) -> TagResponse:
    # Only allow moderators or admins to update tags
    if current_user.role not in ["moderator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators and admins can update tags",
        )

    try:
        tag = await Tag.get(id=tag_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    try:
        # Update the tag
        tag.name = tag_data.name
        tag.slug = slugify(tag_data.name)
        await tag.save()
        return TagResponse.model_validate(tag)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A tag with this name already exists",
        )
