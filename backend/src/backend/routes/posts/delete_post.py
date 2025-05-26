# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from tortoise.exceptions import DoesNotExist

# Project-specific imports
from backend.db.models.post import Post
from backend.db.models.user import User
from backend.utils.auth import get_current_user

router = APIRouter()


@router.delete("/{post_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        post = await Post.get(id=post_id).prefetch_related("author")
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check if the current user is the author or an admin
    if str(post.author.id) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this post",
        )

    # Check if the post has replies
    reply_count = await Post.filter(parent_post=post).count()
    if reply_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete post as it has {reply_count} replies",
        )

    # Delete the post
    await post.delete()
