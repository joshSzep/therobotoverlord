from unittest import mock
import uuid

import pytest

from backend.db.models.user_event import UserEvent


@pytest.fixture
def sample_user_id() -> uuid.UUID:
    """Return a sample user ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_ip_address() -> str:
    """Return a sample IP address."""
    return "127.0.0.1"


@pytest.fixture
def sample_user_agent() -> str:
    """Return a sample user agent string."""
    return "TestClient/0.1"


@pytest.mark.asyncio
async def test_log_login_success(
    sample_user_id: uuid.UUID,
    sample_ip_address: str,
    sample_user_agent: str,
) -> None:
    """Test logging a successful login event."""
    with mock.patch("backend.db.models.user_event.UserEvent.create") as mock_create:
        mock_create.return_value = mock.MagicMock()

        await UserEvent.log_login_success(
            sample_user_id,
            sample_ip_address,
            sample_user_agent,
        )

        # Verify UserEvent.create was called with the correct parameters
        mock_create.assert_awaited_once_with(
            user_id=sample_user_id,
            event_type="login_success",
            ip_address=sample_ip_address,
            user_agent=sample_user_agent,
        )


@pytest.mark.asyncio
async def test_log_login_failure_with_user_id(
    sample_user_id: uuid.UUID,
    sample_ip_address: str,
    sample_user_agent: str,
) -> None:
    """Test logging a failed login attempt with a known user ID."""
    with mock.patch("backend.db.models.user_event.UserEvent.create") as mock_create:
        mock_create.return_value = mock.MagicMock()

        await UserEvent.log_login_failure(
            sample_user_id,
            sample_ip_address,
            sample_user_agent,
        )

        # Verify UserEvent.create was called with the correct parameters
        mock_create.assert_awaited_once_with(
            user_id=sample_user_id,
            event_type="login_failure",
            ip_address=sample_ip_address,
            user_agent=sample_user_agent,
        )


@pytest.mark.asyncio
async def test_log_login_failure_without_user_id(
    sample_ip_address: str,
    sample_user_agent: str,
) -> None:
    """Test logging a failed login attempt without a known user ID."""
    with mock.patch("backend.db.models.user_event.UserEvent.create") as mock_create:
        mock_create.return_value = mock.MagicMock()

        await UserEvent.log_login_failure(
            None,
            sample_ip_address,
            sample_user_agent,
        )

        # Verify UserEvent.create was called with the correct parameters
        mock_create.assert_awaited_once_with(
            user_id=None,
            event_type="login_failure",
            ip_address=sample_ip_address,
            user_agent=sample_user_agent,
        )


@pytest.mark.asyncio
async def test_log_logout(
    sample_user_id: uuid.UUID,
    sample_ip_address: str,
    sample_user_agent: str,
) -> None:
    """Test logging a logout event."""
    with mock.patch("backend.db.models.user_event.UserEvent.create") as mock_create:
        mock_create.return_value = mock.MagicMock()

        await UserEvent.log_logout(
            sample_user_id,
            sample_ip_address,
            sample_user_agent,
        )

        # Verify UserEvent.create was called with the correct parameters
        mock_create.assert_awaited_once_with(
            user_id=sample_user_id,
            event_type="logout",
            ip_address=sample_ip_address,
            user_agent=sample_user_agent,
        )


@pytest.mark.asyncio
async def test_log_password_change(
    sample_user_id: uuid.UUID,
    sample_ip_address: str,
    sample_user_agent: str,
) -> None:
    """Test logging a password change event."""
    with mock.patch("backend.db.models.user_event.UserEvent.create") as mock_create:
        mock_create.return_value = mock.MagicMock()

        await UserEvent.log_password_change(
            sample_user_id,
            sample_ip_address,
            sample_user_agent,
        )

        # Verify UserEvent.create was called with the correct parameters
        mock_create.assert_awaited_once_with(
            user_id=sample_user_id,
            event_type="password_change",
            ip_address=sample_ip_address,
            user_agent=sample_user_agent,
        )


@pytest.mark.asyncio
async def test_log_account_lockout(
    sample_user_id: uuid.UUID,
    sample_ip_address: str,
    sample_user_agent: str,
) -> None:
    """Test logging an account lockout event."""
    with mock.patch("backend.db.models.user_event.UserEvent.create") as mock_create:
        mock_create.return_value = mock.MagicMock()

        await UserEvent.log_account_lockout(
            sample_user_id,
            sample_ip_address,
            sample_user_agent,
        )

        # Verify UserEvent.create was called with the correct parameters
        mock_create.assert_awaited_once_with(
            user_id=sample_user_id,
            event_type="account_lockout",
            ip_address=sample_ip_address,
            user_agent=sample_user_agent,
        )


@pytest.mark.asyncio
async def test_user_event_model_fields() -> None:
    """Test basic instantiation of UserEvent with all fields."""
    with mock.patch("backend.db.models.user_event.UserEvent.create") as mock_create:
        # Create a sample event with all fields
        user_id = uuid.uuid4()
        resource_id = uuid.uuid4()
        metadata = {"key": "value"}

        await UserEvent.create(
            user_id=user_id,
            event_type="test_event",
            ip_address="127.0.0.1",
            user_agent="TestAgent",
            resource_type="test_resource",
            resource_id=resource_id,
            metadata=metadata,
        )

        # Verify create was called with all the fields
        mock_create.assert_awaited_once_with(
            user_id=user_id,
            event_type="test_event",
            ip_address="127.0.0.1",
            user_agent="TestAgent",
            resource_type="test_resource",
            resource_id=resource_id,
            metadata=metadata,
        )
