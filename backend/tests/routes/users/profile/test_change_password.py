from typing import Generator
from unittest import mock
import uuid

from fastapi import status
from fastapi.testclient import TestClient
import pytest

from backend.app import app
from backend.db.models.user import User
from backend.routes.users.users_schemas import PasswordChangeRequestSchema
from backend.utils.auth import get_current_user
from backend.utils.constants import UNKNOWN_IP_ADDRESS_MARKER


@pytest.fixture
def mock_user() -> mock.Mock:
    user_id = uuid.uuid4()

    mock_user = mock.Mock(spec=User)
    mock_user.id = user_id
    mock_user.verify_password = mock.AsyncMock()
    mock_user.set_password = mock.AsyncMock()
    mock_user.save = mock.AsyncMock()

    return mock_user


@pytest.fixture
def password_data() -> PasswordChangeRequestSchema:
    return PasswordChangeRequestSchema(
        current_password="current_password123",
        new_password="new_password123",
    )


@pytest.fixture
def client(mock_user) -> Generator[TestClient, None, None]:
    # Override the get_current_user dependency
    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    # Yield the test client
    client = TestClient(app)
    yield client

    # Clean up after test
    app.dependency_overrides = {}


def test_change_password_success(
    client: TestClient,
    mock_user: mock.Mock,
    password_data: PasswordChangeRequestSchema,
) -> None:
    # Setup mock behavior
    mock_user.verify_password.return_value = True

    # Mock validate_password to return valid
    with (
        mock.patch(
            "backend.routes.users.profile.change_password.validate_password",
            return_value=(True, ""),
        ),
        mock.patch(
            "backend.db.models.user_event.UserEvent.log_password_change",
            new_callable=mock.AsyncMock,
        ) as mock_log_password_change,
    ):
        # Call the endpoint
        response = client.post(
            "/users/profile/change-password",
            json={
                "current_password": password_data.current_password,
                "new_password": password_data.new_password,
            },
        )

        # Verify status code
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify mock calls
        mock_user.verify_password.assert_awaited_once_with(
            password_data.current_password
        )
        mock_user.set_password.assert_awaited_once_with(password_data.new_password)
        mock_user.save.assert_awaited_once()
        mock_log_password_change.assert_awaited_once_with(
            mock_user.id,
            mock.ANY,  # IP address
            mock.ANY,  # User agent
        )


def test_change_password_incorrect_current_password(
    client: TestClient,
    mock_user: mock.Mock,
    password_data: PasswordChangeRequestSchema,
) -> None:
    # Setup mock behavior
    mock_user.verify_password.return_value = False

    # Call the endpoint
    response = client.post(
        "/users/profile/change-password",
        json={
            "current_password": password_data.current_password,
            "new_password": password_data.new_password,
        },
    )

    # Verify status code and response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "CITIZEN, YOUR CURRENT PASSWORD IS INCORRECT"

    # Verify mock calls
    mock_user.verify_password.assert_awaited_once_with(password_data.current_password)
    mock_user.set_password.assert_not_awaited()
    mock_user.save.assert_not_awaited()


def test_change_password_invalid_new_password(
    client: TestClient,
    mock_user: mock.Mock,
    password_data: PasswordChangeRequestSchema,
) -> None:
    # Setup mock behavior
    mock_user.verify_password.return_value = True
    error_message = "Password too short"

    # Mock validate_password to return invalid
    with mock.patch(
        "backend.routes.users.profile.change_password.validate_password",
        return_value=(False, error_message),
    ):
        # Call the endpoint
        response = client.post(
            "/users/profile/change-password",
            json={
                "current_password": password_data.current_password,
                "new_password": password_data.new_password,
            },
        )

        # Verify status code and response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        detail = f"CITIZEN, YOUR NEW PASSWORD REQUIRES CALIBRATION: {error_message}"
        assert response.json()["detail"] == detail

        # Verify mock calls
        mock_user.verify_password.assert_awaited_once_with(
            password_data.current_password
        )
        mock_user.set_password.assert_not_awaited()
        mock_user.save.assert_not_awaited()


def test_change_password_no_client_info(
    client: TestClient,
    mock_user: mock.Mock,
    password_data: PasswordChangeRequestSchema,
) -> None:
    # Setup mock behavior
    mock_user.verify_password.return_value = True

    # Mock validate_password to return valid and mock request.client to be None
    with (
        mock.patch(
            "backend.routes.users.profile.change_password.validate_password",
            return_value=(True, ""),
        ),
        mock.patch(
            "backend.db.models.user_event.UserEvent.log_password_change",
            new_callable=mock.AsyncMock,
        ) as mock_log_password_change,
        mock.patch(
            "fastapi.Request.client",
            new_callable=mock.PropertyMock,
            return_value=None,
        ),
    ):
        # Call the endpoint
        response = client.post(
            "/users/profile/change-password",
            json={
                "current_password": password_data.current_password,
                "new_password": password_data.new_password,
            },
        )

        # Verify status code
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify UserEvent.log_password_change was called with UNKNOWN_IP_ADDRESS_MARKER
        mock_log_password_change.assert_awaited_once_with(
            mock_user.id,
            UNKNOWN_IP_ADDRESS_MARKER,
            mock.ANY,  # User agent
        )


def test_change_password_no_user_agent(
    client: TestClient,
    mock_user: mock.Mock,
    password_data: PasswordChangeRequestSchema,
) -> None:
    # Setup mock behavior
    mock_user.verify_password.return_value = True

    # Mock validate_password to return valid
    with (
        mock.patch(
            "backend.routes.users.profile.change_password.validate_password",
            return_value=(True, ""),
        ),
        mock.patch(
            "backend.db.models.user_event.UserEvent.log_password_change",
            new_callable=mock.AsyncMock,
        ) as mock_log_password_change,
    ):
        # Call the endpoint without User-Agent header
        response = client.post(
            "/users/profile/change-password",
            json={
                "current_password": password_data.current_password,
                "new_password": password_data.new_password,
            },
            headers={"User-Agent": ""},  # Empty User-Agent
        )

        # Verify status code
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify UserEvent.log_password_change was called with empty user_agent
        call_args = mock_log_password_change.await_args[0]  # type: ignore
        assert call_args[0] == mock_user.id  # user_id
        assert call_args[2] == ""  # user_agent (empty string)
