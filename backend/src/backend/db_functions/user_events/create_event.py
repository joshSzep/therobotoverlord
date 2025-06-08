# Standard library imports
from typing import Any
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_event_to_schema
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventResponse


async def create_event(
    event_type: str,
    user_id: Optional[UUID] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> UserEventResponse:
    event = await UserEvent.create(
        user_id=user_id,
        event_type=event_type,
        ip_address=ip_address,
        user_agent=user_agent,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata=metadata,
    )
    return await user_event_to_schema(event)
