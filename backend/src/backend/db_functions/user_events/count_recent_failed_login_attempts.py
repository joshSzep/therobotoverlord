# Standard library imports
from datetime import timedelta
from uuid import UUID

# Project-specific imports
from backend.db.models.user_event import UserEvent
from backend.utils.datetime import now_utc


async def count_recent_failed_login_attempts(
    user_id: UUID,
    hours: int = 24,
) -> int:
    time_threshold = now_utc() - timedelta(hours=hours)

    return (
        await UserEvent.filter(
            user_id=user_id,
            event_type="login",
            created_at__gte=time_threshold,
        )
        .filter(metadata__contains={"success": False})
        .count()
    )
