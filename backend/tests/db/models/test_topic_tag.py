import pytest
from slugify import slugify

from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.db.models.topic_tag import TopicTag
from backend.db.models.user import User


@pytest.mark.asyncio
async def test_topic_tag_create() -> None:
    # Arrange
    user = User(
        email="test@example.com",
        display_name="Test User",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Test Topic",
        author=user,
    )
    await topic.save()

    tag = Tag(name="Test Tag", slug=slugify("Test Tag"))
    await tag.save()

    # Act
    topic_tag = TopicTag(topic=topic, tag=tag)
    await topic_tag.save()

    # Assert
    assert topic_tag.id is not None
    topic_relation = await topic_tag.topic
    assert topic_relation.id == topic.id
    tag_relation = await topic_tag.tag
    assert tag_relation.id == tag.id
    assert topic_tag.created_at is not None
    assert topic_tag.updated_at is not None


@pytest.mark.asyncio
async def test_topic_tag_unique_constraint() -> None:
    # Arrange
    user = User(
        email="test2@example.com",
        display_name="Test User 2",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Another Test Topic",
        author=user,
    )
    await topic.save()

    tag = Tag(name="Another Test Tag", slug=slugify("Another Test Tag"))
    await tag.save()

    topic_tag = TopicTag(topic=topic, tag=tag)
    await topic_tag.save()

    # Act & Assert
    duplicate_topic_tag = TopicTag(topic=topic, tag=tag)
    with pytest.raises(Exception):
        await duplicate_topic_tag.save()


@pytest.mark.asyncio
async def test_topic_tag_delete() -> None:
    # Arrange
    user = User(
        email="test3@example.com",
        display_name="Test User 3",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Topic for Delete Test",
        author=user,
    )
    await topic.save()

    tag = Tag(name="Tag for Delete Test", slug=slugify("Tag for Delete Test"))
    await tag.save()

    topic_tag = TopicTag(topic=topic, tag=tag)
    await topic_tag.save()
    topic_tag_id = topic_tag.id

    # Act
    await topic_tag.delete()

    # Assert
    retrieved_topic_tag = await TopicTag.get_or_none(id=topic_tag_id)
    assert retrieved_topic_tag is None


@pytest.mark.asyncio
async def test_topic_tag_cascade_delete_topic() -> None:
    # Arrange
    user = User(
        email="test4@example.com",
        display_name="Test User 4",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Topic for Cascade Delete",
        author=user,
    )
    await topic.save()

    tag = Tag(name="Tag for Cascade Test", slug=slugify("Tag for Cascade Test"))
    await tag.save()

    topic_tag = TopicTag(topic=topic, tag=tag)
    await topic_tag.save()
    topic_tag_id = topic_tag.id

    # Act - Delete the topic
    await topic.delete()

    # Assert - TopicTag should be deleted due to cascade
    retrieved_topic_tag = await TopicTag.get_or_none(id=topic_tag_id)
    assert retrieved_topic_tag is None


@pytest.mark.asyncio
async def test_topic_tag_cascade_delete_tag() -> None:
    # Arrange
    user = User(
        email="test5@example.com",
        display_name="Test User 5",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Another Topic for Cascade Test",
        author=user,
    )
    await topic.save()

    tag = Tag(
        name="Another Tag for Cascade Test",
        slug=slugify("Another Tag for Cascade Test"),
    )
    await tag.save()

    topic_tag = TopicTag(topic=topic, tag=tag)
    await topic_tag.save()
    topic_tag_id = topic_tag.id

    # Act - Delete the tag
    await tag.delete()

    # Assert - TopicTag should be deleted due to cascade
    retrieved_topic_tag = await TopicTag.get_or_none(id=topic_tag_id)
    assert retrieved_topic_tag is None
