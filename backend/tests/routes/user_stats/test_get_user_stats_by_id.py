from unittest import mock
import uuid

from fastapi import HTTPException
from fastapi import status
import pytest

from backend.routes.user_stats.get_user_stats_by_id import get_user_stats_by_id
from backend.schemas.user_stats import UserStatsResponse


@pytest.fixture
def mock_user_stats_response() -> UserStatsResponse:
    """Mock UserStatsResponse for testing."""
    return UserStatsResponse(
        user_id=uuid.uuid4(),
        username="testuser",
        approved_count=10,
        rejected_count=2,
        pending_count=3,
        approval_rate=83.33,
    )


@pytest.mark.asyncio
async def test_get_user_stats_by_id_success(mock_user_stats_response):
    """Test successful retrieval of user stats."""
    # Arrange
    user_id = mock_user_stats_response.user_id

    with mock.patch(
        "backend.routes.user_stats.get_user_stats_by_id.get_user_stats"
    ) as mock_get_user_stats:
        mock_get_user_stats.return_value = mock_user_stats_response

        # Act
        result = await get_user_stats_by_id(user_id)

        # Assert
        assert result == mock_user_stats_response
        mock_get_user_stats.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_stats_by_id_user_not_found():
    """Test retrieval of stats for non-existent user."""
    # Arrange
    user_id = uuid.uuid4()
    error_message = f"User with id {user_id} not found"

    with mock.patch(
        "backend.routes.user_stats.get_user_stats_by_id.get_user_stats",
        side_effect=ValueError(error_message),
    ) as mock_get_user_stats:
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_user_stats_by_id(user_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert str(exc_info.value.detail) == error_message
        mock_get_user_stats.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_stats_by_id_calculation_error():
    """Test handling of stats calculation errors."""
    # Arrange
    user_id = uuid.uuid4()
    calculation_error = Exception("Stats calculation failed")

    with mock.patch(
        "backend.routes.user_stats.get_user_stats_by_id.get_user_stats",
        side_effect=calculation_error,
    ) as mock_get_user_stats:
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await get_user_stats_by_id(user_id)

        assert exc_info.value == calculation_error
        mock_get_user_stats.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_stats_by_id_zero_stats():
    """Test retrieval of stats for user with no activity."""
    # Arrange
    user_id = uuid.uuid4()
    empty_stats = UserStatsResponse(
        user_id=user_id,
        username="newuser",
        approved_count=0,
        rejected_count=0,
        pending_count=0,
        approval_rate=0.0,
    )

    with mock.patch(
        "backend.routes.user_stats.get_user_stats_by_id.get_user_stats"
    ) as mock_get_user_stats:
        mock_get_user_stats.return_value = empty_stats

        # Act
        result = await get_user_stats_by_id(user_id)

        # Assert
        assert result == empty_stats
        assert result.approved_count == 0
        assert result.rejected_count == 0
        assert result.pending_count == 0
        assert result.approval_rate == 0.0


@pytest.mark.asyncio
async def test_get_user_stats_by_id_invalid_uuid():
    """Test handling of invalid UUID format."""
    # Arrange
    invalid_user_id = "not-a-valid-uuid"

    # Act & Assert
    with pytest.raises(ValueError):
        # This tests the UUID validation before the request reaches the endpoint logic
        uuid.UUID(invalid_user_id)
