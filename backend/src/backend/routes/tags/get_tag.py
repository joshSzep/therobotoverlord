# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.repositories.tag_repository import TagRepository
from backend.routes.tags.schemas import TagResponse

router = APIRouter()


@router.get("/{tag_id}/", response_model=TagResponse)
async def get_tag(tag_id: UUID) -> TagResponse:
    tag = await TagRepository.get_tag_by_id(str(tag_id))

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return TagResponse.model_validate(tag)
