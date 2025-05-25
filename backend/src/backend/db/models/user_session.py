"""User session model for tracking active sessions."""

from tortoise import fields

from backend.db.base import BaseModel
from backend.utils.datetime import now


class UserSession(BaseModel):
    """User session model for tracking active sessions."""

    user = fields.ForeignKeyField("models.User", related_name="sessions")
    ip_address = fields.CharField(max_length=45)  # IPv6 can be up to 45 chars
    user_agent = fields.CharField(max_length=255)
    session_token = fields.CharField(max_length=255)
    expires_at = fields.DatetimeField()
    is_active = fields.BooleanField(default=True)

    async def invalidate(self) -> None:
        """Invalidate the session."""
        self.is_active = False
        await self.save()

    @classmethod
    async def cleanup_expired(cls) -> int:
        """Clean up expired sessions.

        Returns:
            int: Number of sessions cleaned up.
        """
        count = await cls.filter(
            expires_at__lt=now(),
            is_active=True,
        ).update(is_active=False)

        return count
