"""
End-to-end tests for the authentication flow.
"""

from uuid import uuid4

import httpx
import pytest


@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_register_user(api_client: httpx.AsyncClient):
    """Test user registration."""
    # Generate unique user data
    unique_id = uuid4().hex[:8]
    user_data = {
        "email": f"test-user-{unique_id}@example.com",
        "password": "Password123!",
        "display_name": f"Test User {unique_id}",
    }

    # Register the user
    response = await api_client.post("/auth/register/", json=user_data)

    # Assert response
    assert response.status_code == 201
    user = response.json()
    assert user["email"] == user_data["email"]
    assert user["display_name"] == user_data["display_name"]
    assert "id" in user
    assert "password" not in user
    assert user["is_verified"] is False
    assert user["is_locked"] is False
    assert user["role"] == "user"


@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_login_with_valid_credentials(api_client: httpx.AsyncClient, test_user):
    """Test login with valid credentials."""
    # Login data
    login_data = {
        "email": test_user["user_data"]["email"],
        "password": test_user["user_data"]["password"],
    }

    # Login
    response = await api_client.post("/auth/login/", json=login_data)

    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_login_with_invalid_credentials(api_client: httpx.AsyncClient, test_user):
    """Test login with invalid credentials."""
    # Login data with wrong password
    login_data = {
        "email": test_user["user_data"]["email"],
        "password": "WrongPassword123!",
    }

    # Login
    response = await api_client.post("/auth/login/", json=login_data)

    # Assert response
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_get_profile(authenticated_client: httpx.AsyncClient, test_user):
    """Test getting user profile."""
    # Get profile
    response = await authenticated_client.get("/profile/me/")

    # Assert response
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == test_user["user_data"]["email"]
    assert user["display_name"] == test_user["user_data"]["display_name"]
    assert user["id"] == test_user["user_id"]


@pytest.mark.asyncio
@pytest.mark.skip(reason="SQLite configuration needs to be fixed")
async def test_logout(authenticated_client: httpx.AsyncClient):
    """Test user logout."""
    # Logout
    response = await authenticated_client.post("/profile/logout/")

    # Assert response
    assert response.status_code == 204

    # Verify token is invalidated by trying to access profile
    profile_response = await authenticated_client.get("/profile/me/")

    # The token should be invalidated after logout
    assert profile_response.status_code == 401
