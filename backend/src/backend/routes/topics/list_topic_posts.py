# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

# Project-specific imports
from backend.db_functions.posts import list_posts
from backend.db_functions.topics import get_topic_by_id
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse

router = APIRouter()


@router.get("/{topic_id}/posts/", response_model=PostList)
async def list_topic_posts(
    topic_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PostList:
    # Verify that the topic exists
    topic = await get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Get posts for this topic
    post_list = await list_posts(
        skip=skip,
        limit=limit,
        topic_id=topic_id,
    )

    # Filter to only include top-level posts (no parent)
    top_level_posts: list[PostResponse] = []
    for post in post_list.posts:
        if post.parent_post_id is None:
            top_level_posts.append(post)

    return PostList(posts=top_level_posts, count=len(top_level_posts))
