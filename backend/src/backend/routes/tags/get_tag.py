# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from tortoise.exceptions import DoesNotExist

# Project-specific imports
from backend.db.models.tag import Tag
from backend.routes.tags.schemas import TagResponse

router = APIRouter()


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: UUID) -> TagResponse:
    try:
        tag = await Tag.get(id=tag_id)
        return TagResponse.model_validate(tag)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
