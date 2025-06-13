# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
import pytest

# Project-specific imports
from backend.converters.user_schema_to_response import user_schema_to_response
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_user_schema() -> mock.MagicMock:
    """Create a mock user schema for testing."""
    user_schema = mock.MagicMock(spec=UserSchema)
    user_schema.id = uuid.uuid4()
    user_schema.email = "test@example.com"
    user_schema.display_name = "Test User"
    user_schema.is_verified = True
    user_schema.last_login = datetime.now()
    user_schema.role = "user"
    user_schema.is_locked = False
    user_schema.created_at = datetime.now()
    user_schema.updated_at = datetime.now()
    user_schema.approved_count = 5
    user_schema.rejected_count = 2
    return user_schema


@pytest.mark.asyncio
async def test_user_schema_to_response_basic(mock_user_schema):
    """Test basic conversion of a user schema to a response."""
    # Act
    result = await user_schema_to_response(mock_user_schema)

    # Assert
    assert isinstance(result, UserResponse)
    assert result.id == mock_user_schema.id
    assert result.email == mock_user_schema.email
    assert result.display_name == mock_user_schema.display_name
    assert result.is_verified == mock_user_schema.is_verified
    assert result.last_login == mock_user_schema.last_login
    assert result.role == mock_user_schema.role
    assert result.is_locked == mock_user_schema.is_locked
    assert result.created_at == mock_user_schema.created_at
    assert result.updated_at == mock_user_schema.updated_at
    assert result.approved_count == mock_user_schema.approved_count
    assert result.rejected_count == mock_user_schema.rejected_count


@pytest.mark.asyncio
async def test_user_schema_to_response_none_input():
    """Test conversion with None input."""
    # Act
    result = await user_schema_to_response(None)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_user_schema_to_response_different_roles():
    """Test conversion with different user roles."""
    # Arrange
    roles = ["user", "moderator", "admin"]

    for role in roles:
        # Create mock user schema with specific role
        user_schema = mock.MagicMock(spec=UserSchema)
        user_schema.id = uuid.uuid4()
        user_schema.email = f"{role}@example.com"
        user_schema.display_name = f"Test {role.capitalize()}"
        user_schema.role = role
        user_schema.is_verified = True
        user_schema.last_login = datetime.now()
        user_schema.is_locked = False
        user_schema.created_at = datetime.now()
        user_schema.updated_at = datetime.now()
        user_schema.approved_count = 5
        user_schema.rejected_count = 2

        # Act
        result = await user_schema_to_response(user_schema)

        # Assert
        assert result.role == role


@pytest.mark.asyncio
async def test_user_schema_to_response_locked_user():
    """Test conversion with a locked user."""
    # Arrange
    user_schema = mock.MagicMock(spec=UserSchema)
    user_schema.id = uuid.uuid4()
    user_schema.email = "locked@example.com"
    user_schema.display_name = "Locked User"
    user_schema.is_verified = True
    user_schema.last_login = datetime.now()
    user_schema.role = "user"
    user_schema.is_locked = True  # User is locked
    user_schema.created_at = datetime.now()
    user_schema.updated_at = datetime.now()
    user_schema.approved_count = 0
    user_schema.rejected_count = 10

    # Act
    result = await user_schema_to_response(user_schema)

    # Assert
    assert result.is_locked is True


@pytest.mark.asyncio
async def test_user_schema_to_response_missing_fields():
    """Test conversion with missing optional fields in the user schema."""
    # Arrange
    # Create a minimal user schema with only required fields
    user_schema = mock.MagicMock(spec=UserSchema)
    user_schema.id = uuid.uuid4()
    user_schema.email = "minimal@example.com"
    user_schema.display_name = (
        "Minimal User"  # display_name is required in UserResponse
    )
    user_schema.is_verified = False
    user_schema.last_login = None  # Missing last login (optional)
    user_schema.role = "user"
    user_schema.is_locked = False
    user_schema.created_at = datetime.now()
    user_schema.updated_at = datetime.now()
    user_schema.approved_count = 0
    user_schema.rejected_count = 0

    # Act
    result = await user_schema_to_response(user_schema)

    # Assert
    assert result.display_name == "Minimal User"
    assert result.last_login is None


@pytest.mark.asyncio
async def test_user_schema_to_response_with_counts():
    """Test conversion with different approval/rejection counts."""
    # Arrange
    test_counts = [
        (0, 0),  # New user, no activity
        (10, 5),  # More approvals than rejections
        (5, 10),  # More rejections than approvals
        (100, 100),  # Equal high counts
    ]

    for approved, rejected in test_counts:
        # Create mock user schema with specific counts
        user_schema = mock.MagicMock(spec=UserSchema)
        user_schema.id = uuid.uuid4()
        user_schema.email = "test@example.com"
        user_schema.display_name = "Test User"
        user_schema.is_verified = True
        user_schema.last_login = datetime.now()
        user_schema.role = "user"
        user_schema.is_locked = False
        user_schema.created_at = datetime.now()
        user_schema.updated_at = datetime.now()
        user_schema.approved_count = approved
        user_schema.rejected_count = rejected

        # Act
        result = await user_schema_to_response(user_schema)

        # Assert
        assert result.approved_count == approved
        assert result.rejected_count == rejected
