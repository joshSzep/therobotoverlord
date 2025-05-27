# Standard library imports
from typing import Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.repositories.post_repository import PostRepository
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse

router = APIRouter()


@router.get("/", response_model=PostList)
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    topic_id: Optional[UUID] = None,
    author_id: Optional[UUID] = None,
) -> PostList:
    # Use repository to get posts with filters
    posts, count = await PostRepository.list_posts(
        skip=skip, limit=limit, topic_id=topic_id, author_id=author_id
    )

    # Prepare response with reply counts
    post_responses: list[PostResponse] = []
    for post in posts:
        # Get reply count for each post using repository
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
        post_responses.append(PostResponse.model_validate(post_dict))

    return PostList(posts=post_responses, count=count)
