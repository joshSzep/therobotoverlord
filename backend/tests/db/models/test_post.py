import pytest

from backend.db.models.post import Post
from backend.db.models.topic import Topic
from backend.db.models.user import User


@pytest.mark.asyncio
async def test_post_create() -> None:
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

    # Act
    post = Post(
        content="This is a test post content.",
        author=user,
        topic=topic,
    )
    await post.save()

    # Assert
    assert post.id is not None
    assert post.content == "This is a test post content."
    author = await post.author
    assert author.id == user.id
    topic_obj = await post.topic
    assert topic_obj.id == topic.id
    # Handle the case where parent_post might be None
    parent_post_field = getattr(post, "parent_post", None)
    if parent_post_field is not None:
        parent = await parent_post_field
        assert parent is None
    else:
        assert True  # No parent post as expected
    assert post.created_at is not None
    assert post.updated_at is not None


@pytest.mark.asyncio
async def test_post_create_with_parent() -> None:
    # Arrange
    user = User(
        email="test2@example.com",
        display_name="Test User 2",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Topic for Reply Test",
        author=user,
    )
    await topic.save()

    parent_post = Post(
        content="This is a parent post.",
        author=user,
        topic=topic,
    )
    await parent_post.save()

    # Act
    reply_post = Post(
        content="This is a reply to the parent post.",
        author=user,
        topic=topic,
        parent_post=parent_post,
    )
    await reply_post.save()

    # Assert
    assert reply_post.id is not None
    assert reply_post.content == "This is a reply to the parent post."
    parent = await reply_post.parent_post
    assert parent.id == parent_post.id
    topic_obj = await reply_post.topic
    assert topic_obj.id == topic.id


@pytest.mark.asyncio
async def test_post_update() -> None:
    # Arrange
    user = User(
        email="test3@example.com",
        display_name="Test User 3",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Topic for Update Test",
        author=user,
    )
    await topic.save()

    post = Post(
        content="Original content.",
        author=user,
        topic=topic,
    )
    await post.save()
    original_created_at = post.created_at

    # Act
    post.content = "Updated content."
    await post.save()

    # Assert
    assert post.content == "Updated content."
    assert post.created_at == original_created_at
    assert post.updated_at > original_created_at


@pytest.mark.asyncio
async def test_post_delete() -> None:
    # Arrange
    user = User(
        email="test4@example.com",
        display_name="Test User 4",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Topic for Delete Test",
        author=user,
    )
    await topic.save()

    post = Post(
        content="Post to be deleted.",
        author=user,
        topic=topic,
    )
    await post.save()
    post_id = post.id

    # Act
    await post.delete()

    # Assert
    retrieved_post = await Post.get_or_none(id=post_id)
    assert retrieved_post is None


@pytest.mark.asyncio
async def test_post_cascade_delete_parent() -> None:
    # Arrange
    user = User(
        email="test5@example.com",
        display_name="Test User 5",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Topic for Cascade Test",
        author=user,
    )
    await topic.save()

    parent_post = Post(
        content="Parent post for cascade test.",
        author=user,
        topic=topic,
    )
    await parent_post.save()

    reply_post = Post(
        content="Reply post for cascade test.",
        author=user,
        topic=topic,
        parent_post=parent_post,
    )
    await reply_post.save()
    reply_post_id = reply_post.id

    # Act - Delete the parent post
    await parent_post.delete()

    # Assert - Reply post should be deleted due to cascade
    retrieved_reply = await Post.get_or_none(id=reply_post_id)
    assert retrieved_reply is None


@pytest.mark.asyncio
async def test_post_cascade_delete_topic() -> None:
    # Arrange
    user = User(
        email="test6@example.com",
        display_name="Test User 6",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Another Topic for Cascade Test",
        author=user,
    )
    await topic.save()

    post = Post(
        content="Post for topic cascade test.",
        author=user,
        topic=topic,
    )
    await post.save()
    post_id = post.id

    # Act - Delete the topic
    await topic.delete()

    # Assert - Post should be deleted due to cascade
    retrieved_post = await Post.get_or_none(id=post_id)
    assert retrieved_post is None
