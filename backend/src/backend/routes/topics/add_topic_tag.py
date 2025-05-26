# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.db.models.topic_tag import TopicTag
from backend.routes.auth.schemas import UserSchema
from backend.routes.topics.schemas import TagResponse
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
    topic = await Topic.get_or_none(id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Verify that the tag exists
    tag = await Tag.get_or_none(id=request.tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    # Check if the tag is already associated with the topic
    existing = await TopicTag.get_or_none(topic=topic, tag=tag)
    if existing:
        # Tag already exists, return it
        return TagResponse(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
        )

    # Create the association
    await TopicTag.create(topic=topic, tag=tag)

    # Return the tag
    return TagResponse(
        id=tag.id,
        name=tag.name,
        slug=tag.slug,
    )
