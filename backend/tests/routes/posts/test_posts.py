from httpx import AsyncClient
import pytest

from backend.db.models.post import Post
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


async def create_test_post(user, topic, parent_post=None):
    post = Post(
        content="This is a test post content.",
        author=user,
        topic=topic,
        parent_post=parent_post,
    )
    await post.save()
    return post


@pytest.mark.asyncio
async def test_list_posts(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic = await create_test_topic(user)
    post1 = await create_test_post(user, topic)
    post2 = await create_test_post(user, topic)

    # Act
    response = await client.get("/posts/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 2
    assert any(item["id"] == str(post1.id) for item in data["items"])
    assert any(item["id"] == str(post2.id) for item in data["items"])


@pytest.mark.asyncio
async def test_list_posts_by_topic(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic1 = await create_test_topic(user)
    topic2 = Topic(
        title="Another Topic",
        description="This is another test topic",
        author=user,
    )
    await topic2.save()

    post1 = await create_test_post(user, topic1)
    post2 = await create_test_post(user, topic2)

    # Act
    response = await client.get(f"/posts/?topic_id={topic1.id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert any(item["id"] == str(post1.id) for item in data["items"])
    assert not any(item["id"] == str(post2.id) for item in data["items"])


@pytest.mark.asyncio
async def test_get_post(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic = await create_test_topic(user)
    post = await create_test_post(user, topic)

    # Act
    response = await client.get(f"/posts/{post.id}/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(post.id)
    assert data["content"] == post.content
    assert data["author"]["id"] == str(user.id)
    assert data["topic"]["id"] == str(topic.id)
    assert data["parent_post"] is None


@pytest.mark.asyncio
async def test_get_nonexistent_post(client: AsyncClient):
    # Act
    response = await client.get("/posts/00000000-0000-0000-0000-000000000000/")

    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, auth_headers):
    # Arrange
    user = await User.get(email="test@example.com")
    topic = await create_test_topic(user)
    post_data = {
        "content": "This is a new post created via API",
        "topic_id": str(topic.id),
    }

    # Act
    response = await client.post("/posts/", json=post_data, headers=auth_headers)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == post_data["content"]
    assert data["topic"]["id"] == post_data["topic_id"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "author" in data
    assert data["parent_post"] is None


@pytest.mark.asyncio
async def test_create_reply_post(client: AsyncClient, auth_headers):
    # Arrange
    user = await User.get(email="test@example.com")
    topic = await create_test_topic(user)
    parent_post = await create_test_post(user, topic)

    post_data = {
        "content": "This is a reply to the parent post",
        "topic_id": str(topic.id),
        "parent_post_id": str(parent_post.id),
    }

    # Act
    response = await client.post("/posts/", json=post_data, headers=auth_headers)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == post_data["content"]
    assert data["topic"]["id"] == post_data["topic_id"]
    assert data["parent_post"]["id"] == post_data["parent_post_id"]


@pytest.mark.asyncio
async def test_create_post_unauthorized(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic = await create_test_topic(user)
    post_data = {
        "content": "This should fail without auth",
        "topic_id": str(topic.id),
    }

    # Act
    response = await client.post("/posts/", json=post_data)

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_post(client: AsyncClient, auth_headers):
    # Arrange
    user = await User.get(email="test@example.com")
    topic = await create_test_topic(user)
    post = await create_test_post(user, topic)
    update_data = {
        "content": "This is updated content",
    }

    # Act
    response = await client.put(
        f"/posts/{post.id}/", json=update_data, headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == update_data["content"]
    assert data["id"] == str(post.id)


@pytest.mark.asyncio
async def test_update_post_unauthorized(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic = await create_test_topic(user)
    post = await create_test_post(user, topic)
    update_data = {
        "content": "This should fail without auth",
    }

    # Act
    response = await client.put(f"/posts/{post.id}/", json=update_data)

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_post(client: AsyncClient, auth_headers):
    # Arrange
    user = await User.get(email="test@example.com")
    topic = await create_test_topic(user)
    post = await create_test_post(user, topic)

    # Act
    response = await client.delete(f"/posts/{post.id}/", headers=auth_headers)

    # Assert
    assert response.status_code == 204

    # Verify post was deleted
    deleted_post = await Post.get_or_none(id=post.id)
    assert deleted_post is None


@pytest.mark.asyncio
async def test_delete_post_unauthorized(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic = await create_test_topic(user)
    post = await create_test_post(user, topic)

    # Act
    response = await client.delete(f"/posts/{post.id}/")

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_topic_posts(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic = await create_test_topic(user)
    post1 = await create_test_post(user, topic)
    post2 = await create_test_post(user, topic)

    # Create a reply post (should not be returned in top-level posts)
    reply_post = await create_test_post(user, topic, parent_post=post1)

    # Act
    response = await client.get(f"/topics/{topic.id}/posts/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 2  # Only top-level posts
    assert any(item["id"] == str(post1.id) for item in data["items"])
    assert any(item["id"] == str(post2.id) for item in data["items"])
    assert not any(item["id"] == str(reply_post.id) for item in data["items"])


@pytest.mark.asyncio
async def test_get_post_replies(client: AsyncClient):
    # Arrange
    user = await create_test_user()
    topic = await create_test_topic(user)
    parent_post = await create_test_post(user, topic)
    reply1 = await create_test_post(user, topic, parent_post=parent_post)
    reply2 = await create_test_post(user, topic, parent_post=parent_post)

    # Act
    response = await client.get(f"/posts/{parent_post.id}/replies/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 2
    assert any(item["id"] == str(reply1.id) for item in data["items"])
    assert any(item["id"] == str(reply2.id) for item in data["items"])
