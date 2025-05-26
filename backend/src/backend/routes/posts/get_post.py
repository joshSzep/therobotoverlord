# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from tortoise.exceptions import DoesNotExist

# Project-specific imports
from backend.db.models.post import Post
from backend.routes.posts.schemas import PostResponse

router = APIRouter()


@router.get("/{post_id}/", response_model=PostResponse)
async def get_post(post_id: UUID) -> PostResponse:
    try:
        post = await Post.get(id=post_id).prefetch_related("author", "topic")
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

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
