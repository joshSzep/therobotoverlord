"""Tests for the get_me endpoint."""

import datetime
from unittest import mock
import uuid

from fastapi import status
from fastapi.testclient import TestClient
import pytest

from backend.app import app
from backend.db.models.user import User
from backend.routes.users.users_schemas import UserSchema
from backend.utils.auth import get_current_user


@pytest.fixture
def mock_user() -> User:
    """Return a mock user for testing."""
    user_id = uuid.uuid4()
    now = datetime.datetime.now(tz=datetime.UTC)

    mock_user = mock.MagicMock(spec=User)
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.is_verified = True
    mock_user.last_login = now
    mock_user.role = "user"
    mock_user.created_at = now - datetime.timedelta(days=10)
    mock_user.updated_at = now - datetime.timedelta(days=5)

    return mock_user


@pytest.fixture
def client(mock_user: User) -> TestClient:
    """Return a TestClient instance with overridden dependencies."""

    # Override the get_current_user dependency
    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    # Yield the test client
    client = TestClient(app)
    yield client

    # Clean up after test
    app.dependency_overrides = {}


def test_get_current_user_info(client: TestClient, mock_user: User) -> None:
    """Test that the get_current_user_info endpoint returns correct user information."""
    # Call the endpoint
    response = client.get("/users/profile/me")

    # Verify status code
    assert response.status_code == status.HTTP_200_OK

    # Verify response structure
    user_data = response.json()
    assert isinstance(user_data, dict)

    # Verify all fields are included and match the mock_user attributes
    assert user_data["id"] == str(mock_user.id)
    assert user_data["email"] == mock_user.email
    assert user_data["display_name"] == mock_user.display_name
    assert user_data["is_verified"] == mock_user.is_verified
    assert (
        "last_login" in user_data
    )  # Just check presence as datetime formatting makes exact comparison tricky
    assert user_data["role"] == mock_user.role
    assert "created_at" in user_data
    assert "updated_at" in user_data

    # Test that all expected fields from UserSchema are present
    user_schema = UserSchema(
        id=mock_user.id,
        email=mock_user.email,
        display_name=mock_user.display_name,
        is_verified=mock_user.is_verified,
        last_login=mock_user.last_login,
        role=mock_user.role,
        created_at=mock_user.created_at,
        updated_at=mock_user.updated_at,
    )

    # Make sure all expected fields are in the response
    schema_fields = user_schema.model_dump().keys()
    for field in schema_fields:
        assert field in user_data
