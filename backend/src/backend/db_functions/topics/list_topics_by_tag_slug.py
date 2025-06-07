# Standard library imports

# Project-specific imports
from backend.converters import topic_to_schema
from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.schemas.topic import TopicList
from backend.schemas.topic import TopicResponse


async def list_topics_by_tag_slug(
    tag_slug: str,
    skip: int = 0,
    limit: int = 20,
) -> TopicList:
    """
    List topics that have the specified tag slug.

    Args:
        tag_slug: The slug of the tag to filter by
        skip: Number of topics to skip (for pagination)
        limit: Maximum number of topics to return

    Returns:
        TopicList containing the filtered topics and total count
    """
    # Get the tag by slug
    tag = await Tag.get_or_none(slug=tag_slug)

    if not tag:
        # Return empty list if tag doesn't exist
        return TopicList(topics=[], count=0)

    # Query topics that have this tag using a join
    topics = (
        await Topic.filter(topic_tags__tag_id=tag.id)
        .offset(skip)
        .limit(limit)
        .prefetch_related("author")
    )

    # Count total topics with this tag
    count = await Topic.filter(topic_tags__tag_id=tag.id).count()

    # Convert ORM models to schema objects using async converter
    topic_responses: list[TopicResponse] = []
    for topic in topics:
        topic_responses.append(await topic_to_schema(topic))

    return TopicList(topics=topic_responses, count=count)
