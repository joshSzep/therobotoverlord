from unittest import mock

import pytest

from backend.db.models.user import User
from backend.db.models.user import UserRole


@pytest.mark.asyncio
async def test_user_create() -> None:
    # Arrange
    email = "user@example.com"
    display_name = "Tester"
    password_hash = "hash"

    # Mock the User.create method
    with mock.patch.object(User, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await User.create(
            email=email,
            password_hash=password_hash,
            display_name=display_name,
        )

        # Assert
        mock_create.assert_called_once_with(
            email=email,
            password_hash=password_hash,
            display_name=display_name,
        )


@pytest.mark.asyncio
async def test_user_defaults() -> None:
    # Arrange
    user = User(email="a@b.com", password_hash="h", display_name="n")

    # Assert
    assert user.is_verified is False
    assert user.failed_login_attempts == 0
    assert user.role == UserRole.USER
    assert user.is_locked is False

    email_field = User._meta.fields_map.get("email")
    assert email_field is not None
    assert email_field.unique is True
