# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
import pytest

# Project-specific imports
from backend.routes.profile.change_password import change_password
from backend.schemas.password import PasswordChangeRequestSchema
from backend.utils.constants import UNKNOWN_IP_ADDRESS_MARKER


@pytest.mark.asyncio
async def test_change_password_success():
    """Test successful password change."""
    # Arrange
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id

    # Create password change request
    password_data = PasswordChangeRequestSchema(
        current_password="OldPassword123!",
        new_password="NewPassword456@",
    )

    # Create mock request
    mock_request = mock.MagicMock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test User Agent"}

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.profile.change_password.verify_user_password",
            new=mock.AsyncMock(return_value=True),
        ) as mock_verify_password,
        mock.patch(
            "backend.routes.profile.change_password.validate_password",
            return_value=(True, None),
        ) as mock_validate_password,
        mock.patch(
            "backend.routes.profile.change_password.set_user_password",
            new=mock.AsyncMock(),
        ) as mock_set_password,
        mock.patch(
            "backend.routes.profile.change_password.log_password_change",
            new=mock.AsyncMock(),
        ) as mock_log_password_change,
    ):
        # Act
        result = await change_password(
            request=mock_request,
            password_data=password_data,
            current_user=mock_user,
        )

        # Assert
        assert result is None  # Function returns None on success

        # Verify function calls
        mock_verify_password.assert_called_once_with(
            user_id, password_data.current_password
        )
        mock_validate_password.assert_called_once_with(password_data.new_password)
        mock_set_password.assert_called_once_with(user_id, password_data.new_password)
        mock_log_password_change.assert_called_once_with(
            user_id, mock_request.client.host, mock_request.headers.get("User-Agent")
        )


@pytest.mark.asyncio
async def test_change_password_incorrect_current_password():
    """Test password change with incorrect current password."""
    # Arrange
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id

    # Create password change request
    password_data = PasswordChangeRequestSchema(
        current_password="WrongPassword123!",
        new_password="NewPassword456@",
    )

    # Create mock request
    mock_request = mock.MagicMock(spec=Request)

    # Mock dependencies - simulate incorrect current password
    with mock.patch(
        "backend.routes.profile.change_password.verify_user_password",
        new=mock.AsyncMock(return_value=False),
    ) as mock_verify_password:
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await change_password(
                request=mock_request,
                password_data=password_data,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "CITIZEN, YOUR CURRENT PASSWORD IS INCORRECT" in excinfo.value.detail

        # Verify function calls
        mock_verify_password.assert_called_once_with(
            user_id, password_data.current_password
        )


@pytest.mark.asyncio
async def test_change_password_invalid_new_password():
    """Test password change with invalid new password."""
    # Arrange
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id

    # Create password change request
    password_data = PasswordChangeRequestSchema(
        current_password="OldPassword123!",
        new_password="weak",  # Invalid password
    )

    # Create mock request
    mock_request = mock.MagicMock(spec=Request)

    # Error message for invalid password
    error_message = "Password must be at least 8 characters long."

    # Mock dependencies - simulate valid current password but invalid new password
    with (
        mock.patch(
            "backend.routes.profile.change_password.verify_user_password",
            new=mock.AsyncMock(return_value=True),
        ) as mock_verify_password,
        mock.patch(
            "backend.routes.profile.change_password.validate_password",
            return_value=(False, error_message),
        ) as mock_validate_password,
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await change_password(
                request=mock_request,
                password_data=password_data,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "CITIZEN, YOUR NEW PASSWORD REQUIRES CALIBRATION" in excinfo.value.detail
        assert error_message in excinfo.value.detail

        # Verify function calls
        mock_verify_password.assert_called_once_with(
            user_id, password_data.current_password
        )
        mock_validate_password.assert_called_once_with(password_data.new_password)


@pytest.mark.asyncio
async def test_change_password_missing_client_info():
    """Test password change with missing client information."""
    # Arrange
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id

    # Create password change request
    password_data = PasswordChangeRequestSchema(
        current_password="OldPassword123!",
        new_password="NewPassword456@",
    )

    # Create mock request with missing client info
    mock_request = mock.MagicMock(spec=Request)
    mock_request.client = None
    mock_request.headers = {}

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.profile.change_password.verify_user_password",
            new=mock.AsyncMock(return_value=True),
        ) as mock_verify_password,
        mock.patch(
            "backend.routes.profile.change_password.validate_password",
            return_value=(True, None),
        ) as mock_validate_password,
        mock.patch(
            "backend.routes.profile.change_password.set_user_password",
            new=mock.AsyncMock(),
        ) as mock_set_password,
        mock.patch(
            "backend.routes.profile.change_password.log_password_change",
            new=mock.AsyncMock(),
        ) as mock_log_password_change,
    ):
        # Act
        result = await change_password(
            request=mock_request,
            password_data=password_data,
            current_user=mock_user,
        )

        # Assert
        assert result is None  # Function returns None on success

        # Verify function calls with fallback values
        mock_verify_password.assert_called_once_with(
            user_id, password_data.current_password
        )
        mock_validate_password.assert_called_once_with(password_data.new_password)
        mock_set_password.assert_called_once_with(user_id, password_data.new_password)
        mock_log_password_change.assert_called_once_with(
            user_id, UNKNOWN_IP_ADDRESS_MARKER, ""
        )
