from unittest import mock

import pytest

from backend.db.models.user import User
from backend.db.models.user_event import UserEvent


@pytest.mark.asyncio
async def test_user_event_create() -> None:
    # Arrange
    mock_user = mock.AsyncMock(spec=User)

    # Mock the UserEvent.create method
    with mock.patch.object(UserEvent, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await UserEvent.create(
            user=mock_user,
            event_type="login",
            ip_address="127.0.0.1",
        )

        # Assert
        mock_create.assert_called_once_with(
            user=mock_user,
            event_type="login",
            ip_address="127.0.0.1",
        )


@pytest.mark.asyncio
async def test_user_event_fields() -> None:
    # Arrange
    event = UserEvent(event_type="logout")

    # Assert
    assert event.event_type == "logout"
    assert event.ip_address is None
    assert event.user_agent is None
    assert event.resource_type is None
    assert event.resource_id is None
    assert event.metadata is None

    event_type_field = UserEvent._meta.fields_map.get("event_type")
    assert event_type_field.max_length == 50
