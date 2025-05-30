from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import status

from backend.db.models.user import User
from backend.db.models.user import UserRole
from backend.db_functions.pending_posts.get_pending_post_by_id import (
    get_pending_post_by_id as db_get_pending_post_by_id,
)
from backend.schemas.pending_post import PendingPostResponse
from backend.utils.auth import get_current_user

router = APIRouter()


@router.get("/{pending_post_id}/", response_model=PendingPostResponse)
async def get_pending_post_by_id(
    pending_post_id: UUID = Path(
        ..., description="The ID of the pending post to retrieve"
    ),
    current_user: User = Depends(get_current_user),
) -> PendingPostResponse:
    pending_post = await db_get_pending_post_by_id(pending_post_id)

    if not pending_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending post not found",
        )

    # If user is not the author and not an admin, deny access
    is_author = str(pending_post.author.id) == str(current_user.id)
    is_admin = current_user.role == UserRole.ADMIN

    if not is_author and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CITIZEN, YOU LACK AUTHORIZATION TO VIEW THIS PENDING POST",
        )

    return pending_post
