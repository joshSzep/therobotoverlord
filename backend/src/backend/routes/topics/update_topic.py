# Standard library imports
from typing import List
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from slugify.slugify import slugify
from tortoise.transactions import atomic

# Project-specific imports
from backend.db.models.user import User
from backend.repositories.tag_repository import TagRepository
from backend.repositories.topic_repository import TopicRepository
from backend.repositories.topic_tag_repository import TopicTagRepository
from backend.routes.topics.schemas import TagResponse
from backend.routes.topics.schemas import TopicResponse
from backend.routes.topics.schemas import TopicUpdate
from backend.utils.auth import get_current_user

router = APIRouter()


@router.put("/{topic_id}/", response_model=TopicResponse)
@atomic()
async def update_topic(
    topic_id: UUID,
    topic_data: TopicUpdate,
    current_user: User = Depends(get_current_user),
) -> TopicResponse:
    # Get the topic
    topic = await TopicRepository.get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Fetch related author
    await topic.fetch_related("author")

    # Check if the current user is the author
    if str(topic.author.id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this topic",
        )

    # Update topic fields if provided
    topic = await TopicRepository.update_topic(
        topic_id=topic_id,
        title=topic_data.title,
        description=topic_data.description,
    )
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found after update",
        )

    # Update tags if provided
    if topic_data.tags is not None:
        # Process tags
        tag_ids: List[UUID] = []
        for tag_name in topic_data.tags:
            # Try to find existing tag or create a new one
            tag = await TagRepository.get_tag_by_slug(slugify(tag_name))
            if not tag:
                tag = await TagRepository.create_tag(tag_name, slugify(tag_name))

            tag_ids.append(tag.id)

        # Set topic tags (this will handle adding new ones and removing old ones)
        await TopicTagRepository.set_topic_tags(topic.id, tag_ids)

    # Get tags for the topic
    tags_list = await TopicTagRepository.get_tags_for_topic(topic.id)

    # Convert to TagResponse objects
    tags = [
        TagResponse(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
        )
        for tag in tags_list
    ]

    # Create the response object
    topic_response = TopicResponse.model_validate(topic)
    topic_response.tags = tags

    return topic_response
