# Project-specific imports
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventSchema


async def user_event_to_schema(event: UserEvent) -> UserEventSchema:
    # We need to handle the user relation to get the user_id
    await event.fetch_related("user")

    # Create the schema with explicit type annotations
    schema = UserEventSchema(
        id=event.id,
        user_id=None,  # We'll set this separately
        event_type=event.event_type,
        ip_address=event.ip_address,
        user_agent=event.user_agent,
        resource_type=event.resource_type,
        resource_id=event.resource_id,
        metadata={},  # We'll set this separately
        created_at=event.created_at,
        updated_at=event.updated_at,
    )

    # Set the user_id field after creation
    if hasattr(event, "user") and event.user is not None:
        schema.user_id = event.user.id

    # Set the metadata field after creation
    if hasattr(event, "metadata") and event.metadata is not None:
        schema.metadata = event.metadata

    return schema
