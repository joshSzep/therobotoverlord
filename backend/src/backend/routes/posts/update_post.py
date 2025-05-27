# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db.models.user import User
from backend.repositories.post_repository import PostRepository
from backend.schemas.post import PostResponse
from backend.schemas.post import PostUpdate
from backend.utils.auth import get_current_user

router = APIRouter()


@router.put("/{post_id}/", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
) -> PostResponse:
    # Check if post exists
    post = await PostRepository.get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check if the current user is the author or an admin
    is_author = await PostRepository.is_user_post_author(post_id, current_user.id)
    if not is_author and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this post",
        )

    # Update the post using repository
    updated_post = await PostRepository.update_post(post_id, post_data.content)
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to update post",
        )

    return updated_post
