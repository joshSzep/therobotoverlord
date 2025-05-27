# Standard library imports
from datetime import timedelta
from typing import List
from uuid import UUID

# Project-specific imports
from backend.converters import user_event_to_schema
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventSchema
from backend.utils.datetime import now_utc


async def get_recent_failed_login_attempts(
    user_id: UUID,
    hours: int = 24,
    limit: int = 10,
) -> List[UserEventSchema]:
    time_threshold = now_utc() - timedelta(hours=hours)

    events = (
        await UserEvent.filter(
            user_id=user_id,
            event_type="login",
            created_at__gte=time_threshold,
        )
        .filter(metadata__contains={"success": False})
        .order_by("-created_at")
        .limit(limit)
    )

    # Convert ORM models to schema objects using async converter
    event_schemas: list[UserEventSchema] = []
    for event in events:
        event_schemas.append(await user_event_to_schema(event))

    return event_schemas
