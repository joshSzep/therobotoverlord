import pytest

from backend.db.models.topic import Topic
from backend.db.models.user import User


@pytest.mark.asyncio
async def test_topic_create() -> None:
    # Arrange
    user = User(
        email="test@example.com",
        display_name="Test User",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    # Act
    topic = Topic(
        title="Test Topic",
        author=user,
        description="This is a test topic",
    )
    await topic.save()

    # Assert
    assert topic.id is not None
    assert topic.title == "Test Topic"
    assert topic.description == "This is a test topic"
    assert topic.author.id == user.id
    assert topic.created_at is not None
    assert topic.updated_at is not None


@pytest.mark.asyncio
async def test_topic_create_without_description() -> None:
    # Arrange
    user = User(
        email="test2@example.com",
        display_name="Test User 2",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    # Act
    topic = Topic(
        title="Test Topic Without Description",
        author=user,
    )
    await topic.save()

    # Assert
    assert topic.id is not None
    assert topic.title == "Test Topic Without Description"
    assert topic.description is None
    assert topic.author.id == user.id


@pytest.mark.asyncio
async def test_topic_update() -> None:
    # Arrange
    user = User(
        email="test3@example.com",
        display_name="Test User 3",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Original Title",
        author=user,
        description="Original description",
    )
    await topic.save()
    original_created_at = topic.created_at

    # Act
    topic.title = "Updated Title"
    topic.description = "Updated description"
    await topic.save()

    # Assert
    assert topic.title == "Updated Title"
    assert topic.description == "Updated description"
    assert topic.created_at == original_created_at
    assert topic.updated_at > original_created_at


@pytest.mark.asyncio
async def test_topic_delete() -> None:
    # Arrange
    user = User(
        email="test4@example.com",
        display_name="Test User 4",
        # Hashed version of 'password123'
        password_hash="$2b$12$ESPjqYxCxpBgSKoJRJkVBOKcL8Bduj0QDcYp5Ic.cXEvrpMB5/Jn.",
    )
    await user.save()

    topic = Topic(
        title="Topic to Delete",
        author=user,
    )
    await topic.save()
    topic_id = topic.id

    # Act
    await topic.delete()

    # Assert
    retrieved_topic = await Topic.get_or_none(id=topic_id)
    assert retrieved_topic is None
