# Standard library imports
from typing import Optional

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.repositories.tag_repository import TagRepository
from backend.repositories.topic_repository import TopicRepository
from backend.repositories.topic_tag_repository import TopicTagRepository
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
    # Get topics with pagination
    topics = []
    count = 0

    # Filter by tag if provided
    if tag:
        # Find the tag by name or slug
        db_tag = await TagRepository.get_tag_by_slug(tag)
        if not db_tag:
            db_tag = await TagRepository.get_tag_by_name(tag)
        if db_tag:
            # Get topics that have this tag
            topic_list = await TopicTagRepository.get_topics_for_tag(db_tag.id)
            # Apply pagination manually
            count = len(topic_list)
            topics = topic_list[skip : skip + limit]
            # Fetch related author for each topic
            for topic in topics:
                await topic.fetch_related("author")
    else:
        # Get all topics with pagination
        topics, count = await TopicRepository.list_topics(skip=skip, limit=limit)
        # Fetch related author for each topic
        for topic in topics:
            await topic.fetch_related("author")

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

        # Get tags for this topic
        topic_tags = await TopicTagRepository.get_tags_for_topic(topic.id)
        tags = [
            TagResponse(
                id=tag.id,
                name=tag.name,
                slug=tag.slug,
            )
            for tag in topic_tags
        ]

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
