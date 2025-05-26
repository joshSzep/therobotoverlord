from httpx import AsyncClient
import pytest

from backend.db.models.tag import Tag


async def create_test_tag():
    tag = Tag(name="Test Tag")
    await tag.save()
    return tag


@pytest.mark.asyncio
async def test_list_tags(client: AsyncClient):
    # Arrange
    tag1 = await create_test_tag()
    tag2 = Tag(name="Another Tag")
    await tag2.save()

    # Act
    response = await client.get("/tags/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 2
    assert any(item["id"] == str(tag1.id) for item in data["items"])
    assert any(item["id"] == str(tag2.id) for item in data["items"])


@pytest.mark.asyncio
async def test_get_tag(client: AsyncClient):
    # Arrange
    tag = await create_test_tag()

    # Act
    response = await client.get(f"/tags/{tag.id}/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(tag.id)
    assert data["name"] == tag.name
    assert data["slug"] == tag.slug


@pytest.mark.asyncio
async def test_get_nonexistent_tag(client: AsyncClient):
    # Act
    response = await client.get("/tags/00000000-0000-0000-0000-000000000000/")

    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_tag(client: AsyncClient, auth_headers):
    # Arrange
    tag_data = {
        "name": "New Tag",
    }

    # Act
    response = await client.post("/tags/", json=tag_data, headers=auth_headers)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == tag_data["name"]
    assert data["slug"] == "new-tag"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_tag_unauthorized(client: AsyncClient):
    # Arrange
    tag_data = {
        "name": "Unauthorized Tag",
    }

    # Act
    response = await client.post("/tags/", json=tag_data)

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_tag(client: AsyncClient, auth_headers):
    # Arrange
    tag = await create_test_tag()
    update_data = {
        "name": "Updated Tag Name",
    }

    # Act
    response = await client.put(
        f"/tags/{tag.id}/", json=update_data, headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["slug"] == "updated-tag-name"
    assert data["id"] == str(tag.id)


@pytest.mark.asyncio
async def test_update_tag_unauthorized(client: AsyncClient):
    # Arrange
    tag = await create_test_tag()
    update_data = {
        "name": "Unauthorized Update",
    }

    # Act
    response = await client.put(f"/tags/{tag.id}/", json=update_data)

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_tag(client: AsyncClient, auth_headers):
    # Arrange
    tag = await create_test_tag()

    # Act
    response = await client.delete(f"/tags/{tag.id}/", headers=auth_headers)

    # Assert
    assert response.status_code == 204

    # Verify tag was deleted
    deleted_tag = await Tag.get_or_none(id=tag.id)
    assert deleted_tag is None


@pytest.mark.asyncio
async def test_delete_tag_unauthorized(client: AsyncClient):
    # Arrange
    tag = await create_test_tag()

    # Act
    response = await client.delete(f"/tags/{tag.id}/")

    # Assert
    assert response.status_code == 401
