# Standard library imports
from typing import List
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from slugify.slugify import slugify
from tortoise.transactions import atomic

# Project-specific imports
from backend.db.models.user import User
from backend.db_functions.tags import create_tag
from backend.db_functions.tags import get_tag_by_slug
from backend.db_functions.topic_tags import add_tags_to_topic
from backend.db_functions.topic_tags import get_tags_for_topic
from backend.db_functions.topics import create_topic as db_create_topic
from backend.schemas.tag import TagResponse
from backend.schemas.topic import TopicCreate
from backend.schemas.topic import TopicResponse
from backend.schemas.user import UserSchema
from backend.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
@atomic()
async def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_user),
) -> TopicResponse:
    # Create the topic
    topic = await db_create_topic(
        title=topic_data.title,
        description=topic_data.description or "",  # Ensure description is not None
        created_by_id=current_user.id,
    )

    # Process tags
    tag_ids: List[UUID] = []
    for tag_name in topic_data.tags:
        # Try to find existing tag or create a new one
        tag = await get_tag_by_slug(slugify(tag_name))
        if not tag:
            tag = await create_tag(tag_name, slugify(tag_name))

        tag_ids.append(tag.id)

    # Create topic-tag relationships
    try:
        await add_tags_to_topic(topic.id, tag_ids)
    except Exception as e:
        # Log the error but continue processing
        print(f"Error creating topic-tag relationships: {e}")

    # Get the author information
    author = current_user

    # Create the response object with proper model conversion

    # Create UserSchema instance for the author
    author_schema = UserSchema(
        id=author.id,
        email=author.email,
        display_name=author.display_name,
        is_verified=author.is_verified,
        last_login=author.last_login,
        role=author.role,
        created_at=author.created_at,
        updated_at=author.updated_at,
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
    tags = await get_tags_for_topic(topic.id)
    for tag in tags:
        topic_response.tags.append(
            TagResponse(
                id=tag.id,
                name=tag.name,
                slug=tag.slug,
            )
        )

    return topic_response
