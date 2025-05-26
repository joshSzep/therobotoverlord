# Standard library imports
from typing import Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.db.models.post import Post
from backend.routes.posts.schemas import PostList
from backend.routes.posts.schemas import PostResponse

router = APIRouter()


@router.get("/", response_model=PostList)
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    topic_id: Optional[UUID] = None,
    author_id: Optional[UUID] = None,
) -> PostList:
    # Build query with filters
    query = Post.all().prefetch_related("author", "topic")

    if topic_id:
        query = query.filter(topic__id=topic_id)

    if author_id:
        query = query.filter(author_id=author_id)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    posts = await query.offset(skip).limit(limit)

    # Prepare response with reply counts
    post_responses: list[PostResponse] = []
    for post in posts:
        # Get reply count for each post
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
        post_responses.append(PostResponse.model_validate(post_dict))

    return PostList(posts=post_responses, count=count)
