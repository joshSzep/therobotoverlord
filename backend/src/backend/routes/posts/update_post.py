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
from backend.routes.posts.schemas import PostResponse
from backend.routes.posts.schemas import PostUpdate
from backend.utils.auth import get_current_user

router = APIRouter()


@router.put("/{post_id}/", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
) -> PostResponse:
    try:
        post = await Post.get(id=post_id).prefetch_related("author", "topic")
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check if the current user is the author or an admin
    if str(post.author.id) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this post",
        )

    # Update the post
    post.content = post_data.content
    await post.save()

    # Get reply count
    reply_count = await Post.filter(parent_post_id=post.id).count()

    # Create response object
    post_dict = {
        "id": post.id,
        "content": post.content,
        "author": post.author,
        "topic_id": post.topic.id,
        "parent_post_id": post.parent_post.id if post.parent_post else None,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "reply_count": reply_count,
    }

    return PostResponse.model_validate(post_dict)
