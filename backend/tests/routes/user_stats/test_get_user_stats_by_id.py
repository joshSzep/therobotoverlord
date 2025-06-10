from unittest import mock
import uuid

from fastapi import HTTPException
import pytest

from backend.routes.user_stats.get_user_stats_by_id import get_user_stats_by_id
from backend.schemas.user_stats import UserStatsResponse


@pytest.fixture
def mock_user_stats() -> UserStatsResponse:
    """Returns a mock UserStatsResponse object."""
    user_id = uuid.uuid4()
    return UserStatsResponse(
        user_id=user_id,
        username="testuser",
        approved_count=10,
        rejected_count=3,
        pending_count=2,
        approval_rate=10 / 13 if 13 > 0 else 0,
    )


@pytest.mark.asyncio
async def test_get_user_stats_by_id_success(mock_user_stats):
    """Test successful retrieval of user statistics."""
    # Arrange
    user_id = mock_user_stats.user_id

    # Mock dependencies
    with mock.patch(
        "backend.routes.user_stats.get_user_stats_by_id.get_user_stats",
        new=mock.AsyncMock(return_value=mock_user_stats),
    ) as mock_get_stats:
        # Act
        result = await get_user_stats_by_id(user_id=user_id)

        # Assert
        assert result == mock_user_stats
        assert result.user_id == user_id
        assert result.approved_count == 10
        assert result.rejected_count == 3
        assert result.pending_count == 2
        mock_get_stats.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_stats_by_id_user_not_found():
    """Test handling of non-existent user."""
    # Arrange
    user_id = uuid.uuid4()
    error_message = f"User with ID {user_id} not found"

    # Mock dependencies
    with mock.patch(
        "backend.routes.user_stats.get_user_stats_by_id.get_user_stats",
        new=mock.AsyncMock(side_effect=ValueError(error_message)),
    ) as mock_get_stats:
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_user_stats_by_id(user_id=user_id)

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert error_message in excinfo.value.detail
        mock_get_stats.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_stats_by_id_zero_counts():
    """Test retrieval of user statistics with zero counts."""
    # Arrange
    user_id = uuid.uuid4()
    zero_stats = UserStatsResponse(
        user_id=user_id,
        username="zerouser",
        approved_count=0,
        rejected_count=0,
        pending_count=0,
        approval_rate=0.0,
    )

    # Mock dependencies
    with mock.patch(
        "backend.routes.user_stats.get_user_stats_by_id.get_user_stats",
        new=mock.AsyncMock(return_value=zero_stats),
    ) as mock_get_stats:
        # Act
        result = await get_user_stats_by_id(user_id=user_id)

        # Assert
        assert result == zero_stats
        assert result.user_id == user_id
        assert result.approved_count == 0
        assert result.rejected_count == 0
        assert result.pending_count == 0
        mock_get_stats.assert_called_once_with(user_id)
