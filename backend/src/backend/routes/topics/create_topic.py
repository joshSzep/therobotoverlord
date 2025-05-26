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
from backend.routes.auth.schemas import UserSchema
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

        try:
            # Create the topic-tag relationship
            await TopicTag.create(topic=topic, tag=tag)
        except Exception as e:
            # Log the error but continue processing
            print(f"Error creating topic-tag relationship: {e}")
            # We'll still include the tag in the response

    # Fetch the author relation only - we'll handle tags separately
    await topic.fetch_related("author")

    # Create the response object with proper model conversion

    # Create UserSchema instance for the author
    author_schema = UserSchema(
        id=topic.author.id,
        email=topic.author.email,
        display_name=topic.author.display_name,
        is_verified=topic.author.is_verified,
        last_login=topic.author.last_login,
        role=topic.author.role,
        created_at=topic.author.created_at,
        updated_at=topic.author.updated_at,
    )

    # Create the TopicResponse with the proper UserSchema
    topic_response = TopicResponse(
        id=topic.id,
        title=topic.title,
        description=topic.description,
        author=author_schema,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        tags=[],
    )

    # Add tags to the response
    for tag_name in topic_data.tags:
        # Find the tag we created earlier
        tag = await Tag.get(name=tag_name)
        # Add it to the response
        topic_response.tags.append(
            TagResponse(
                id=tag.id,
                name=tag.name,
                slug=tag.slug,
            )
        )

    return topic_response
