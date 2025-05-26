from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from slugify.slugify import slugify
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic

from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.db.models.topic_tag import TopicTag
from backend.db.models.user import User
from backend.routes.topics.schemas import TagResponse
from backend.routes.topics.schemas import TopicCreate
from backend.routes.topics.schemas import TopicList
from backend.routes.topics.schemas import TopicResponse
from backend.routes.topics.schemas import TopicUpdate
from backend.utils.auth import get_current_user

router = APIRouter(tags=["topics"])


@router.get("/", response_model=TopicList)
async def list_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    tag: Optional[str] = None,
) -> TopicList:
    query = Topic.all().prefetch_related("author", "topic_tags__tag")

    if tag:
        # Filter by tag if provided
        query = query.filter(topic_tags__tag__slug=tag)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    topics = await query.offset(skip).limit(limit)

    # Convert to response model
    topic_responses: list[TopicResponse] = []
    for topic in topics:
        # Extract tags from the prefetched topic_tags relation
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
        topic_responses.append(topic_response)

    return TopicList(topics=topic_responses, count=count)


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
@atomic()
async def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_user),
) -> TopicResponse:
    # Create the topic
    topic = await Topic.create(
        title=topic_data.title,
        description=topic_data.description,
        author=current_user,
    )

    # Process tags
    for tag_name in topic_data.tags:
        # Try to find existing tag or create a new one
        tag, _ = await Tag.get_or_create(
            name=tag_name,
            defaults={"slug": slugify(tag_name)},
        )

        # Create the topic-tag relationship
        await TopicTag.create(topic=topic, tag=tag)

    # Fetch the complete topic with related data
    await topic.fetch_related("author", "topic_tags__tag")

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


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: UUID) -> TopicResponse:
    try:
        topic = await Topic.get(id=topic_id).prefetch_related(
            "author", "topic_tags__tag"
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

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


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
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
            detail="You don't have permission to delete this topic",
        )

    # Delete the topic (this will also delete related topic_tags due to cascading)
    await topic.delete()
