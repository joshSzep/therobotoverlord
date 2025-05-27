# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.repositories.post_repository import PostRepository
from backend.schemas.post import PostResponse

router = APIRouter()


@router.get("/{post_id}/", response_model=PostResponse)
async def get_post(post_id: UUID) -> PostResponse:
    # Get post using repository
    post = await PostRepository.get_post_by_id(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Get reply count using repository
    reply_count = await PostRepository.get_reply_count(post.id)

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
