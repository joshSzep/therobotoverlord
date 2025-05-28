# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

from backend.db.models.user import User

# Project-specific imports
from backend.db_functions.users.update_user import update_user
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_user() -> mock.MagicMock:
    user = mock.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.display_name = "Test User"
    user.is_verified = False
    user.last_login = None
    user.role = "user"
    user.is_locked = False
    user.created_at = mock.MagicMock()
    user.updated_at = mock.MagicMock()
    user.save = mock.AsyncMock()
    return user


@pytest.fixture
def mock_user_schema(mock_user) -> UserSchema:
    return UserSchema(
        id=mock_user.id,
        email=mock_user.email,
        display_name=mock_user.display_name,
        is_verified=mock_user.is_verified,
        role=mock_user.role,
        is_locked=mock_user.is_locked,
        created_at=mock_user.created_at,
        updated_at=mock_user.updated_at,
        last_login=mock_user.last_login,
    )


@pytest.mark.asyncio
async def test_update_user_success_full_update(mock_user, mock_user_schema) -> None:
    # Arrange
    test_id = mock_user.id
    new_display_name = "Updated Name"
    new_email = "updated@example.com"

    # Mock the database query - RULE #10 compliance: only operates on User model
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.update_user.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
    ):
        # Act
        result = await update_user(
            user_id=test_id, display_name=new_display_name, email=new_email
        )

        # Assert
        assert result is not None
        assert result.id == mock_user.id
        # Skip datetime comparisons as they may cause issues with mock objects

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        assert mock_user.display_name == new_display_name
        assert mock_user.email == new_email
        mock_user.save.assert_called_once()
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_update_user_success_display_name_only(
    mock_user, mock_user_schema
) -> None:
    # Arrange
    test_id = mock_user.id
    new_display_name = "Updated Name"
    original_email = mock_user.email

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.update_user.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
    ):
        # Act
        result = await update_user(user_id=test_id, display_name=new_display_name)

        # Assert
        assert result is not None
        assert result.id == mock_user.id

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        assert mock_user.display_name == new_display_name
        assert mock_user.email == original_email  # Email should not change
        mock_user.save.assert_called_once()
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_update_user_success_email_only(mock_user, mock_user_schema) -> None:
    # Arrange
    test_id = mock_user.id
    new_email = "updated@example.com"
    original_display_name = mock_user.display_name

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.update_user.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
    ):
        # Act
        result = await update_user(user_id=test_id, email=new_email)

        # Assert
        assert result is not None
        assert result.id == mock_user.id

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        # Display name should not change
        assert mock_user.display_name == original_display_name
        assert mock_user.email == new_email
        mock_user.save.assert_called_once()
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_update_user_no_changes(mock_user, mock_user_schema) -> None:
    # Arrange
    test_id = mock_user.id
    original_display_name = mock_user.display_name
    original_email = mock_user.email

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.update_user.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
    ):
        # Act
        result = await update_user(user_id=test_id)

        # Assert
        assert result is not None
        assert result.id == mock_user.id

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        assert mock_user.display_name == original_display_name
        assert mock_user.email == original_email
        mock_user.save.assert_called_once()  # Save is still called even with no changes
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_update_user_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()
    new_display_name = "Updated Name"
    new_email = "updated@example.com"

    # Mock the database query
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await update_user(
            user_id=test_id, display_name=new_display_name, email=new_email
        )

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_update_user_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    new_display_name = "Updated Name"
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await update_user(user_id=test_id, display_name=new_display_name)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_update_user_save_error(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    new_display_name = "Updated Name"
    save_error = IntegrityError("Error saving user")
    mock_user.save.side_effect = save_error

    # Mock the database query
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await update_user(user_id=test_id, display_name=new_display_name)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_get.assert_called_once_with(id=test_id)
        assert mock_user.display_name == new_display_name
        mock_user.save.assert_called_once()
