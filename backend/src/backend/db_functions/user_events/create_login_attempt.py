# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_event_to_schema
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventSchema


async def create_login_attempt(
    user_id: Optional[UUID],
    ip_address: str,
    user_agent: str,
    success: bool,
) -> UserEventSchema:
    # Create a user event with login information
    event = await UserEvent.create(
        user_id=user_id,
        event_type="login",
        ip_address=ip_address,
        user_agent=user_agent,
        metadata={"success": success},
    )
    return await user_event_to_schema(event)
