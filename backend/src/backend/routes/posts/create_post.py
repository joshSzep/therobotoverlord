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
from backend.schemas.post import PostCreate
from backend.schemas.post import PostResponse
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
    if post_data.parent_post_id:
        parent_post = await PostRepository.get_post_by_id(post_data.parent_post_id)
        if not parent_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent post not found",
            )

        # Check if parent post belongs to the same topic
        if str(parent_post.topic_id) != str(post_data.topic_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent post must belong to the same topic",
            )

    try:
        # Create the post using repository
        return await PostRepository.create_post(
            content=post_data.content,
            author_id=current_user.id,
            topic_id=post_data.topic_id,
            parent_post_id=post_data.parent_post_id,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
