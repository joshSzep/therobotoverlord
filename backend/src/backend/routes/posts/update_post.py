# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db.models.user import User
from backend.db_functions.posts import get_post_by_id
from backend.db_functions.posts import update_post as db_update_post
from backend.schemas.post import PostResponse
from backend.schemas.post import PostUpdate
from backend.utils.role_check import get_moderator_user

router = APIRouter()


@router.put("/{post_id}/", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    post_data: PostUpdate,
    current_user: User = Depends(get_moderator_user),
) -> PostResponse:
    # Check if post exists
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # No need to check authorship since we're already restricting to moderators/admins

    # Update the post using data access function
    updated_post = await db_update_post(post_id, post_data.content)
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to update post",
        )

    return updated_post
