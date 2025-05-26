# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from slugify.slugify import slugify
from tortoise.transactions import atomic

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.db.models.topic_tag import TopicTag
from backend.db.models.user import User
from backend.routes.topics.schemas import TagResponse
from backend.routes.topics.schemas import TopicCreate
from backend.routes.topics.schemas import TopicResponse
from backend.utils.auth import get_current_user

router = APIRouter()


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
