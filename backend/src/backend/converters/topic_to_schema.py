from backend.converters.tag_to_schema import tag_to_schema
from backend.converters.user_to_schema import user_to_schema
from backend.db.models.post import Post
from backend.db.models.topic import Topic
from backend.schemas.tag import TagResponse
from backend.schemas.topic import TopicResponse


async def topic_to_schema(topic: Topic) -> TopicResponse:
    # Fetch related data
    await topic.fetch_related("author", "topic_tags__tag")

    # Calculate post count for this topic (including all posts, not just top-level)
    post_count = await Post.filter(topic_id=topic.id).count()

    # Convert tags to schema objects
    tag_responses: list[TagResponse] = []
    for topic_tag in topic.topic_tags:
        tag_responses.append(await tag_to_schema(topic_tag.tag))

    return TopicResponse(
        id=topic.id,
        title=topic.title,
        description=topic.description,
        author=await user_to_schema(topic.author),
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        tags=tag_responses,
        post_count=post_count,
    )
