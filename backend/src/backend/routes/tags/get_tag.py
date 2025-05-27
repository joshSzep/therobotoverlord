# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.repositories.tag_repository import TagRepository
from backend.schemas.tag import TagResponse

router = APIRouter()


@router.get("/{tag_id}/", response_model=TagResponse)
async def get_tag(tag_id: UUID) -> TagResponse:
    # The repository now returns a TagResponse object directly
    tag = await TagRepository.get_tag_by_id(tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return tag
