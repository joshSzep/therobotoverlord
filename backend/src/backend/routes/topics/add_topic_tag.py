# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel

# Project-specific imports
from backend.repositories.tag_repository import TagRepository
from backend.repositories.topic_repository import TopicRepository
from backend.repositories.topic_tag_repository import TopicTagRepository
from backend.schemas.tag import TagResponse
from backend.schemas.user import UserSchema
from backend.utils.auth import get_current_user

router = APIRouter()


class AddTagRequest(BaseModel):
    tag_id: UUID


@router.post("/{topic_id}/tags/", response_model=TagResponse)
async def add_topic_tag(
    topic_id: UUID,
    request: AddTagRequest,
    current_user: UserSchema = Depends(get_current_user),
) -> TagResponse:
    # Verify that the topic exists
    topic = await TopicRepository.get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Verify that the tag exists
    tag = await TagRepository.get_tag_by_id(request.tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    # Check if the tag is already associated with the topic
    existing = await TopicTagRepository.get_topic_tag(topic_id, request.tag_id)
    if existing:
        # Tag already exists, return it
        return TagResponse(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
        )

    # Create the association
    await TopicTagRepository.create_topic_tag(topic_id, request.tag_id)

    # Return the tag
    return TagResponse(
        id=tag.id,
        name=tag.name,
        slug=tag.slug,
    )
