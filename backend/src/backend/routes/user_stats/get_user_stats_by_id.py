from uuid import UUID

from fastapi import HTTPException
from fastapi import status

from backend.db_functions.user_stats.get_user_stats import get_user_stats
from backend.routes.user_stats import router
from backend.schemas.user_stats import UserStatsResponse


@router.get("/{user_id}/", response_model=UserStatsResponse)
async def get_user_stats_by_id(
    user_id: UUID,
) -> UserStatsResponse:
    """
    Get a user's statistics including approved, rejected, and pending post counts.
    """
    try:
        return await get_user_stats(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
