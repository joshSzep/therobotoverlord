# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.auth.register import register
from backend.schemas.user import UserSchema


@pytest.mark.asyncio
async def test_register_success():
    """Test successful user registration."""
    # Arrange
    user_id = uuid.uuid4()
    email = "new_user@example.com"
    password = "StrongP@ssw0rd"
    display_name = "New User"

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.email = email
    mock_user.display_name = display_name
    mock_user.is_verified = False
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = datetime(2025, 5, 25)
    mock_user.updated_at = datetime(2025, 5, 25)

    # Create mock UserCreateSchema
    user_data = mock.MagicMock()
    user_data.email = email
    user_data.password = password
    user_data.display_name = display_name

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.auth.register.get_user_by_email",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.routes.auth.register.validate_password",
            return_value=(True, ""),
        ),
        mock.patch(
            "backend.routes.auth.register.create_user",
            new=mock.AsyncMock(return_value=mock_user),
        ) as mock_create_user,
    ):
        # Act
        result = await register(user_data=user_data)

        # Assert
        assert isinstance(result, UserSchema)
        assert result.id == user_id
        assert result.email == email
        assert result.display_name == display_name
        assert result.is_verified is False
        assert result.role == "user"

        # Verify function calls
        mock_create_user.assert_called_once_with(
            email=email,
            password=password,
            display_name=display_name,
        )


@pytest.mark.asyncio
async def test_register_existing_email():
    """Test registration with an existing email."""
    # Arrange
    email = "existing@example.com"
    password = "StrongP@ssw0rd"
    display_name = "Existing User"

    # Create mock existing user
    mock_existing_user = mock.MagicMock()
    mock_existing_user.email = email

    # Create mock UserCreateSchema
    user_data = mock.MagicMock()
    user_data.email = email
    user_data.password = password
    user_data.display_name = display_name

    # Mock dependencies - simulate existing user
    with mock.patch(
        "backend.routes.auth.register.get_user_by_email",
        new=mock.AsyncMock(return_value=mock_existing_user),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await register(user_data=user_data)

        # Verify the exception details
        assert excinfo.value.status_code == 400
        assert "Email already registered" in excinfo.value.detail


@pytest.mark.asyncio
async def test_register_invalid_password():
    """Test registration with an invalid password."""
    # Arrange
    email = "new_user@example.com"
    password = "weak"
    display_name = "New User"

    # Create mock UserCreateSchema
    user_data = mock.MagicMock()
    user_data.email = email
    user_data.password = password
    user_data.display_name = display_name

    # Mock dependencies - simulate invalid password
    with (
        mock.patch(
            "backend.routes.auth.register.get_user_by_email",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.routes.auth.register.validate_password",
            return_value=(False, "Password too weak"),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await register(user_data=user_data)

        # Verify the exception details
        assert excinfo.value.status_code == 400
        assert "Password too weak" in excinfo.value.detail
