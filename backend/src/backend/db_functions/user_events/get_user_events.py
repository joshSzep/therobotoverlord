# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_event_to_schema
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventListSchema
from backend.schemas.user_event import UserEventSchema


async def get_user_events(
    user_id: UUID,
    skip: int = 0,
    limit: int = 20,
    event_type: Optional[str] = None,
) -> UserEventListSchema:
    query = UserEvent.filter(user_id=user_id)

    if event_type:
        query = query.filter(event_type=event_type)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    events = await query.offset(skip).limit(limit).order_by("-created_at")

    # Convert ORM models to schema objects using async converter
    event_schemas: list[UserEventSchema] = []
    for event in events:
        event_schemas.append(await user_event_to_schema(event))

    return UserEventListSchema(user_events=event_schemas, count=count)
