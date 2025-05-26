# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

# Project-specific imports
from backend.db.models.post import Post
from backend.routes.posts.schemas import PostList
from backend.routes.posts.schemas import PostResponse

router = APIRouter()


@router.get("/posts/{post_id}/replies/", response_model=PostList)
async def list_post_replies(
    post_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PostList:
    # Verify that the parent post exists
    parent_post = await Post.get_or_none(id=post_id)
    if not parent_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent post not found",
        )

    # Get replies to the post
    query = Post.filter(parent_post=parent_post).prefetch_related("author", "topic")

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
