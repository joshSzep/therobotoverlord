# Standard library imports
from typing import Annotated
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db.models.user import User
from backend.db.models.user import UserRole
from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id,
)
from backend.schemas.pending_post import PendingPostResponse
from backend.utils.auth import get_current_user

router = APIRouter()


@router.get("/{pending_post_id}/", response_model=PendingPostResponse)
async def get_post_moderation_status(
    pending_post_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> PendingPostResponse:
    # Get the pending post
    pending_post = await get_pending_post_by_id(pending_post_id)

    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending post not found",
        )

    # Check if the user is the author of the post or a moderator/admin
    is_moderator_or_admin = current_user.role in [UserRole.MODERATOR, UserRole.ADMIN]
    is_author = str(pending_post.author.id) == str(current_user.id)
    if not is_author and not is_moderator_or_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this pending post",
        )

    return pending_post
