# Standard library imports
from typing import Optional

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.db.models.topic_tag import TopicTag
from backend.routes.auth.schemas import UserSchema
from backend.routes.topics.schemas import TagResponse
from backend.routes.topics.schemas import TopicList
from backend.routes.topics.schemas import TopicResponse

router = APIRouter()


@router.get("/", response_model=TopicList)
async def list_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    tag: Optional[str] = None,
) -> TopicList:
    # Start with all topics and prefetch the author relation
    query = Topic.all().prefetch_related("author")

    # Filter by tag if provided
    if tag:
        # Find the tag by name or slug
        db_tag = await Tag.get_or_none(name=tag) or await Tag.get_or_none(slug=tag)
        if db_tag:
            # Get topic IDs that have this tag
            topic_tags = await TopicTag.filter(tag=db_tag).prefetch_related("topic")
            topic_ids = [tt.topic.id for tt in topic_tags]
            # Filter topics by these IDs
            query = query.filter(id__in=topic_ids)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    topics = await query.offset(skip).limit(limit)

    # Convert to response model
    topic_responses: list[TopicResponse] = []
    for topic in topics:
        # Create author schema
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

        # For now, we'll use an empty list for tags
        # The topic_tags relation is not properly set up yet
        tags: list[TagResponse] = []

        # Create the response object
        topic_response = TopicResponse(
            id=topic.id,
            title=topic.title,
            description=topic.description,
            author=author_schema,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
            tags=tags,
        )
        topic_responses.append(topic_response)

    return TopicList(topics=topic_responses, count=count)
