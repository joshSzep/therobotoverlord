# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.converters import user_event_to_schema
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventSchema


async def log_password_change(
    user_id: UUID,
    ip_address: str,
    user_agent: str,
) -> UserEventSchema:
    event = await UserEvent.create(
        user_id=user_id,
        event_type="password_change",
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return await user_event_to_schema(event)
