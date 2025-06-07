from uuid import UUID

from backend.db.models.user import User
from backend.db_functions.user_events.create_event import create_event


async def increment_user_approval_count(
    user_id: UUID,
    post_id: UUID,
) -> None:
    """
    Increment the user's approval count and create an event when a post is approved.
    """
    # Get the user
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    # Create a user event for post approval
    await create_event(
        event_type="post_approved",
        user_id=user_id,
        resource_type="post",
        resource_id=post_id,
        metadata={"action": "post_approved"},
    )
