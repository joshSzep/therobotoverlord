# Standard library imports
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from slugify.slugify import slugify
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.db.models.topic_tag import TopicTag
from backend.db.models.user import User
from backend.routes.topics.schemas import TagResponse
from backend.routes.topics.schemas import TopicResponse
from backend.routes.topics.schemas import TopicUpdate
from backend.utils.auth import get_current_user

router = APIRouter()


@router.put("/{topic_id}", response_model=TopicResponse)
@atomic()
async def update_topic(
    topic_id: UUID,
    topic_data: TopicUpdate,
    current_user: User = Depends(get_current_user),
) -> TopicResponse:
    try:
        topic = await Topic.get(id=topic_id).prefetch_related("author")
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Check if the current user is the author
    if str(topic.author.id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this topic",
        )

    # Update topic fields if provided
    if topic_data.title is not None:
        topic.title = topic_data.title

    if topic_data.description is not None:
        topic.description = topic_data.description

    await topic.save()

    # Update tags if provided
    if topic_data.tags is not None:
        # Remove existing topic-tag relationships
        await TopicTag.filter(topic_id=topic.id).delete()

        # Create new topic-tag relationships
        for tag_name in topic_data.tags:
            # Try to find existing tag or create a new one
            tag, _ = await Tag.get_or_create(
                name=tag_name,
                defaults={"slug": slugify(tag_name)},
            )

            # Create the topic-tag relationship
            await TopicTag.create(topic=topic, tag=tag)

    # Fetch the updated topic with related data
    await topic.fetch_related("topic_tags__tag")

    # Extract tags from the topic_tags relation
    tags = [
        TagResponse(
            id=tt.tag.id,
            name=tt.tag.name,
            slug=tt.tag.slug,
        )
        for tt in topic.topic_tags
    ]

    # Create the response object
    topic_response = TopicResponse.model_validate(topic)
    topic_response.tags = tags

    return topic_response
