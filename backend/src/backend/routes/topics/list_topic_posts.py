# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

# Project-specific imports
from backend.db.models.post import Post
from backend.db.models.topic import Topic
from backend.routes.posts.schemas import PostList
from backend.routes.posts.schemas import PostResponse
from backend.routes.users.users_schemas import UserSchema

router = APIRouter()


@router.get("/{topic_id}/posts/", response_model=PostList)
async def list_topic_posts(
    topic_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PostList:
    # Verify that the topic exists
    topic = await Topic.get_or_none(id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Get top-level posts (no parent post)
    query = Post.filter(topic=topic, parent_post=None)
    query = query.prefetch_related("author", "topic")

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    posts = await query.offset(skip).limit(limit)

    # Prepare response with reply counts
    post_responses: list[PostResponse] = []
    for post in posts:
        # Get reply count for each post
        reply_count = await Post.filter(parent_post_id=post.id).count()

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
