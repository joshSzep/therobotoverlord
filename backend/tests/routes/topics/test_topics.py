from httpx import AsyncClient
import pytest

from backend.db.models.topic import Topic
from backend.db.models.user import User


async def create_test_user():
    user = User(
        email="test@example.com",
        display_name="Test User",
    )
    await user.set_password("password123")
    await user.save()
    return user


async def create_test_topic(user):
    topic = Topic(
        title="Test Topic",
        description="This is a test topic",
        author=user,
    )
    await topic.save()
    return topic


@pytest.mark.asyncio
async def test_list_topics(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic1 = await create_test_topic(user)
    topic2 = Topic(
        title="Another Topic",
        description="This is another test topic",
        author=user,
    )
    await topic2.save()

    # Act
    response = await client.get("/topics/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 2
    assert any(item["id"] == str(topic1.id) for item in data["items"])
    assert any(item["id"] == str(topic2.id) for item in data["items"])


@pytest.mark.asyncio
async def test_get_topic(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic = await create_test_topic(user)

    # Act
    response = await client.get(f"/topics/{topic.id}/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(topic.id)
    assert data["title"] == topic.title
    assert data["description"] == topic.description
    assert data["author"]["id"] == str(user.id)


@pytest.mark.asyncio
async def test_get_nonexistent_topic(client: AsyncClient):
    # Act
    response = await client.get("/topics/00000000-0000-0000-0000-000000000000/")

    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_topic(client: AsyncClient, auth_headers):
    # Arrange
    topic_data = {
        "title": "New Topic",
        "description": "This is a new topic created via API",
    }

    # Act
    response = await client.post("/topics/", json=topic_data, headers=auth_headers)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == topic_data["title"]
    assert data["description"] == topic_data["description"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "author" in data


@pytest.mark.asyncio
async def test_create_topic_unauthorized(client: AsyncClient):
    # Arrange
    topic_data = {
        "title": "Unauthorized Topic",
        "description": "This should fail without auth",
    }

    # Act
    response = await client.post("/topics/", json=topic_data)

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_topic(client: AsyncClient, auth_headers):
    # Arrange
    user = await User.get(email="test@example.com")
    topic = await create_test_topic(user)
    update_data = {
        "title": "Updated Topic Title",
        "description": "This is an updated description",
    }

    # Act
    response = await client.put(
        f"/topics/{topic.id}/", json=update_data, headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["id"] == str(topic.id)


@pytest.mark.asyncio
async def test_update_topic_unauthorized(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic = await create_test_topic(user)
    update_data = {
        "title": "Unauthorized Update",
        "description": "This should fail without auth",
    }

    # Act
    response = await client.put(f"/topics/{topic.id}/", json=update_data)

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_topic(client: AsyncClient, auth_headers):
    # Arrange
    user = await User.get(email="test@example.com")
    topic = await create_test_topic(user)

    # Act
    response = await client.delete(f"/topics/{topic.id}/", headers=auth_headers)

    # Assert
    assert response.status_code == 204

    # Verify topic was deleted
    deleted_topic = await Topic.get_or_none(id=topic.id)
    assert deleted_topic is None


@pytest.mark.asyncio
async def test_delete_topic_unauthorized(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic = await create_test_topic(user)

    # Act
    response = await client.delete(f"/topics/{topic.id}/")

    # Assert
    assert response.status_code == 401
