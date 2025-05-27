# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_event_to_schema
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventListSchema
from backend.schemas.user_event import UserEventSchema


async def list_login_attempts(
    user_id: Optional[UUID] = None,
    ip_address: Optional[str] = None,
    success: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
) -> UserEventListSchema:
    query = UserEvent.filter(event_type="login")

    if user_id:
        query = query.filter(user_id=user_id)

    if ip_address:
        query = query.filter(ip_address=ip_address)

    if success is not None:
        query = query.filter(metadata__contains={"success": success})

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    attempts = await query.offset(skip).limit(limit).order_by("-created_at")

    # Convert ORM models to schema objects using async converter
    event_schemas: list[UserEventSchema] = []
    for attempt in attempts:
        event_schemas.append(await user_event_to_schema(attempt))

    return UserEventListSchema(events=event_schemas, count=count)
