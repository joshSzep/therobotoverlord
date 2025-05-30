# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db.models.user import User
from backend.db_functions.posts import delete_post as db_delete_post
from backend.db_functions.posts import get_post_by_id
from backend.db_functions.posts import get_reply_count
from backend.utils.role_check import get_moderator_user

router = APIRouter()


@router.delete("/{post_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(get_moderator_user),
) -> None:
    # Check if post exists
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # No need to check authorship since we're already restricting to moderators/admins

    # Check if the post has replies
    reply_count = await get_reply_count(post_id)
    if reply_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete post as it has {reply_count} replies",
        )

    # Delete the post using data access function
    success = await db_delete_post(post_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete post",
        )
