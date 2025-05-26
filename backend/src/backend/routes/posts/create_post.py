# Standard library imports

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from tortoise.exceptions import ValidationError

# Project-specific imports
from backend.db.models.user import User
from backend.repositories.post_repository import PostRepository
from backend.repositories.topic_repository import TopicRepository
from backend.routes.auth.schemas import UserSchema
from backend.routes.posts.schemas import PostCreate
from backend.routes.posts.schemas import PostResponse
from backend.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate, current_user: User = Depends(get_current_user)
) -> PostResponse:
    # Verify that the topic exists
    topic = await TopicRepository.get_topic_by_id(post_data.topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Verify that the parent post exists and belongs to the same topic if provided
    parent_post = None
    if post_data.parent_post_id:
        parent_post = await PostRepository.get_post_by_id(post_data.parent_post_id)
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
        # Create the post using repository
        post = await PostRepository.create_post(
            content=post_data.content,
            author_id=current_user.id,
            topic_id=topic.id,
            parent_post_id=post_data.parent_post_id,
        )

        # Get reply count (should be 0 for a new post)
        reply_count = await PostRepository.get_reply_count(post.id)

        # Create author schema from user model
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

        return post_response
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
