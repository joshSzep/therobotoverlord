# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db_functions.posts import get_post_by_id
from backend.schemas.post import PostResponse

router = APIRouter()


@router.get("/{post_id}/", response_model=PostResponse)
async def get_post(post_id: UUID) -> PostResponse:
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post
