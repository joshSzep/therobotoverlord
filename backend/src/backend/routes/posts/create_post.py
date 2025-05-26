# Standard library imports

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from tortoise.exceptions import ValidationError

# Project-specific imports
from backend.db.models.post import Post
from backend.db.models.topic import Topic
from backend.db.models.user import User
from backend.routes.posts.schemas import PostCreate
from backend.routes.posts.schemas import PostResponse
from backend.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate, current_user: User = Depends(get_current_user)
) -> PostResponse:
    # Verify that the topic exists
    topic = await Topic.get_or_none(id=post_data.topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Verify that the parent post exists and belongs to the same topic if provided
    parent_post = None
    if post_data.parent_post_id:
        parent_post = await Post.get_or_none(id=post_data.parent_post_id)
        if not parent_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent post not found",
            )

        if str(parent_post.topic.id) != str(post_data.topic_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent post must belong to the same topic",
            )

    try:
        # Create the post
        post = await Post.create(
            content=post_data.content,
            author=current_user,
            topic=topic,
            parent_post=parent_post,
        )

        # Fetch related data
        await post.fetch_related("author", "topic")

        # Get reply count (should be 0 for a new post)
        reply_count = await Post.filter(parent_post=post).count()

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
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
