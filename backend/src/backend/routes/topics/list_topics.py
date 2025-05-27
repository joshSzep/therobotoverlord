# Standard library imports
from typing import Optional

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.db_functions.tags import get_tag_by_name
from backend.db_functions.tags import get_tag_by_slug
from backend.db_functions.topic_tags import get_topics_for_tag
from backend.db_functions.topics import list_topics as db_list_topics
from backend.schemas.topic import TopicList

router = APIRouter()


@router.get("/", response_model=TopicList)
async def list_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    tag: Optional[str] = None,
) -> TopicList:
    # Check if filtering by tag
    if tag:
        # Find the tag by name or slug
        db_tag = await get_tag_by_slug(tag)
        if not db_tag:
            db_tag = await get_tag_by_name(tag)

        if db_tag:
            # Get topics that have this tag (now returns TopicResponse objects)
            topic_responses = await get_topics_for_tag(db_tag.id)

            # Apply pagination manually
            count = len(topic_responses)
            paginated_responses = topic_responses[skip : skip + limit]

            return TopicList(topics=paginated_responses, count=count)

        # If tag not found, return empty list
        return TopicList(topics=[], count=0)
    else:
        # Get all topics with pagination using data access function
        return await db_list_topics(skip=skip, limit=limit)
