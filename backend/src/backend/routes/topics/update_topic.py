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
from backend.db_functions.tags import create_tag
from backend.db_functions.tags import get_tag_by_slug
from backend.db_functions.topic_tags import set_topic_tags
from backend.db_functions.topics import get_topic_by_id
from backend.db_functions.topics import is_user_topic_author
from backend.db_functions.topics import update_topic as db_update_topic
from backend.schemas.topic import TopicResponse
from backend.schemas.topic import TopicUpdate
from backend.utils.auth import get_current_user

router = APIRouter()


@router.put("/{topic_id}/", response_model=TopicResponse)
@atomic()
async def update_topic(
    topic_id: UUID,
    topic_data: TopicUpdate,
    current_user: User = Depends(get_current_user),
) -> TopicResponse:
    # Check if topic exists
    topic = await get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Check if the current user is the author
    is_author = await is_user_topic_author(topic_id, current_user.id)
    if not is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this topic",
        )

    # Update topic fields if provided
    updated_topic = await db_update_topic(
        topic_id=topic_id,
        title=topic_data.title,
        description=topic_data.description,
    )
    if not updated_topic:
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
            tag = await get_tag_by_slug(slugify(tag_name))
            if not tag:
                tag = await create_tag(tag_name, slugify(tag_name))

            tag_ids.append(tag.id)

        # Set topic tags (this will handle adding new ones and removing old ones)
        await set_topic_tags(updated_topic.id, tag_ids)

    # Get the updated topic with all relations via data access function
    final_topic = await get_topic_by_id(topic_id)
    if not final_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found after update",
        )
    return final_topic
