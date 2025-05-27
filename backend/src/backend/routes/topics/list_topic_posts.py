# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

# Project-specific imports
from backend.repositories.post_repository import PostRepository
from backend.repositories.topic_repository import TopicRepository
from backend.routes.auth.schemas import UserSchema
from backend.routes.posts.schemas import PostList
from backend.routes.posts.schemas import PostResponse

router = APIRouter()


@router.get("/{topic_id}/posts/", response_model=PostList)
async def list_topic_posts(
    topic_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PostList:
    # Verify that the topic exists
    topic = await TopicRepository.get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Get top-level posts for this topic
    posts, count = await PostRepository.list_posts(
        skip=skip,
        limit=limit,
        topic_id=topic_id,
    )

    # Filter out posts that have a parent (only show top-level posts)
    # We need to fetch the parent_post relation first
    for post in posts:
        await post.fetch_related("parent_post")
    posts = [post for post in posts if post.parent_post is None]

    # Prepare response with reply counts
    post_responses: list[PostResponse] = []
    for post in posts:
        # Get reply count for each post
        reply_count = await PostRepository.get_reply_count(post.id)

        # Create author schema
        author_schema = UserSchema(
            id=post.author.id,
            email=post.author.email,
            display_name=post.author.display_name,
            is_verified=post.author.is_verified,
            last_login=post.author.last_login,
            role=post.author.role,
            created_at=post.author.created_at,
            updated_at=post.author.updated_at,
        )

        # Create response object
        post_response = PostResponse(
            id=post.id,
            content=post.content,
            author=author_schema,
            topic_id=post.topic.id,
            parent_post_id=post.parent_post.id if post.parent_post else None,
            created_at=post.created_at,
            updated_at=post.updated_at,
            reply_count=reply_count,
        )
        post_responses.append(post_response)

    return PostList(posts=post_responses, count=count)
