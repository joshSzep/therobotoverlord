from datetime import datetime
from unittest import mock
import uuid

import pytest

from backend.converters.user_to_schema import user_to_schema
from backend.db.models.user import User
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_user() -> mock.MagicMock:
    user_id = uuid.uuid4()

    # Create mock user
    user = mock.MagicMock(spec=User)
    user.id = user_id
    user.email = "user@example.com"
    user.display_name = "Test User"
    user.is_verified = True
    user.role = "user"
    user.is_locked = False
    user.created_at = datetime.now()
    user.updated_at = datetime.now()
    user.last_login = datetime.now()

    return user


@pytest.mark.asyncio
async def test_user_to_schema(mock_user) -> None:
    # Convert the mock user to a schema
    schema = await user_to_schema(mock_user)

    # Verify the schema has the correct values
    assert isinstance(schema, UserSchema)
    assert schema.id == mock_user.id
    assert schema.email == mock_user.email
    assert schema.display_name == mock_user.display_name
    assert schema.is_verified == mock_user.is_verified
    assert schema.role == mock_user.role
    assert schema.is_locked == mock_user.is_locked
    assert schema.created_at == mock_user.created_at
    assert schema.updated_at == mock_user.updated_at
    assert schema.last_login == mock_user.last_login
