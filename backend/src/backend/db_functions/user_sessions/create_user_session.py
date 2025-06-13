# Standard library imports
from datetime import timedelta
import secrets
from uuid import UUID

# Third-party imports
from tortoise.exceptions import DoesNotExist

# Project-specific imports
from backend.converters.user_session_to_schema import user_session_to_schema
from backend.db.models.user import User
from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSessionSchema
from backend.utils.datetime import now_utc


async def create_user_session(
    user_id: UUID,
    ip_address: str = "0.0.0.0",
    user_agent: str = "Unknown",
    expires_days: int = 7,
) -> UserSessionSchema:
    # Generate a secure token
    token = secrets.token_urlsafe(32)

    # Calculate expiration date
    expires_at = now_utc() + timedelta(days=expires_days)

    try:
        # Get the user
        user = await User.get(id=user_id)

        # Create a new session
        session = await UserSession.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            session_token=token,
            expires_at=expires_at,
            is_active=True,
        )

        # Update user's last login time
        user.last_login = now_utc()
        await user.save()

        # Return the session schema
        return await user_session_to_schema(session)

    except DoesNotExist:
        raise ValueError(f"User with ID {user_id} not found")
