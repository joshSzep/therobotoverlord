"""
End-to-end tests for post-related functionality.
"""

from uuid import uuid4

import httpx
import pytest


# We need to create a topic first before creating posts
@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_create_topic(authenticated_client: httpx.AsyncClient):
    """Test creating a new topic."""
    # Topic data
    topic_data = {
        "title": f"Test Topic {uuid4().hex[:8]}",
        "description": "This is a test topic created during E2E testing.",
    }

    # Create topic
    response = await authenticated_client.post("/topics/", json=topic_data)

    # Assert response
    assert response.status_code == 201
    topic = response.json()
    assert topic["title"] == topic_data["title"]
    assert topic["description"] == topic_data["description"]
    assert "id" in topic

    return topic


@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_create_post(authenticated_client: httpx.AsyncClient):
    """Test creating a new post."""
    # First create a topic
    topic = await test_create_topic(authenticated_client)

    # Post data
    post_data = {
        "content": "This is a test post content created during E2E testing.",
        "topic_id": topic["id"],
    }

    # Create post
    response = await authenticated_client.post("/posts/", json=post_data)

    # Assert response
    assert response.status_code == 201
    post = response.json()
    assert post["content"] == post_data["content"]
    assert post["topic_id"] == topic["id"]
    assert "id" in post
    assert "created_at" in post
    assert "updated_at" in post
    assert "author" in post

    return post


@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_get_post(authenticated_client: httpx.AsyncClient):
    """Test getting a post by ID."""
    # First create a post
    created_post = await test_create_post(authenticated_client)

    # Get the post
    response = await authenticated_client.get(f"/posts/{created_post['id']}/")

    # Assert response
    assert response.status_code == 200
    post = response.json()
    assert post["id"] == created_post["id"]
    assert post["content"] == created_post["content"]
    assert post["topic_id"] == created_post["topic_id"]


@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_update_post(authenticated_client: httpx.AsyncClient):
    """Test updating a post."""
    # First create a post
    created_post = await test_create_post(authenticated_client)

    # Update data
    update_data = {"content": "This post content has been updated during E2E testing."}

    # Update the post
    response = await authenticated_client.put(
        f"/posts/{created_post['id']}/", json=update_data
    )

    # Assert response
    assert response.status_code == 200
    post = response.json()
    assert post["id"] == created_post["id"]
    assert post["content"] == update_data["content"]
    assert post["topic_id"] == created_post["topic_id"]
    assert post["created_at"] == created_post["created_at"]
    assert post["updated_at"] != created_post["updated_at"]


@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_delete_post(authenticated_client: httpx.AsyncClient):
    """Test deleting a post."""
    # First create a post
    created_post = await test_create_post(authenticated_client)

    # Delete the post
    response = await authenticated_client.delete(f"/posts/{created_post['id']}/")

    # Assert response
    assert response.status_code == 204

    # Verify post is deleted
    get_response = await authenticated_client.get(f"/posts/{created_post['id']}/")
    assert get_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_list_posts(authenticated_client: httpx.AsyncClient):
    """Test listing posts."""
    # Create a topic
    topic = await test_create_topic(authenticated_client)

    # Create a few posts in the topic
    for _ in range(3):
        post_data = {
            "content": f"Test post content {uuid4().hex[:8]}",
            "topic_id": topic["id"],
        }
        await authenticated_client.post("/posts/", json=post_data)

    # List posts for the topic
    response = await authenticated_client.get(f"/topics/{topic['id']}/posts/")

    # Assert response
    assert response.status_code == 200
    posts_response = response.json()
    assert "posts" in posts_response
    assert "count" in posts_response
    assert posts_response["count"] == 3
    assert len(posts_response["posts"]) == 3
