# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from slugify import slugify
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db.models.user import User
from backend.routes.tags.schemas import TagCreate
from backend.routes.tags.schemas import TagResponse
from backend.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate, current_user: User = Depends(get_current_user)
) -> TagResponse:
    # Only allow moderators or admins to create tags
    if current_user.role not in ["moderator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators and admins can create tags",
        )

    try:
        # Create the tag
        tag = await Tag.create(
            name=tag_data.name,
            slug=slugify(tag_data.name),
        )
        return TagResponse.model_validate(tag)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A tag with this name already exists",
        )
