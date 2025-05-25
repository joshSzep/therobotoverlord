"""Event model for tracking user activity."""

import uuid

from tortoise import fields

from backend.db.base import BaseModel


class UserEvent(BaseModel):
    """Model for tracking user events and activities."""

    user = fields.ForeignKeyField(  # type: ignore[var-annotated]
        "models.User",
        related_name="events",
        null=True,
    )
    event_type = fields.CharField(max_length=50)
    ip_address = fields.CharField(max_length=45, null=True)
    user_agent = fields.CharField(max_length=255, null=True)
    resource_type = fields.CharField(max_length=50, null=True)
    resource_id = fields.UUIDField(null=True)
    metadata = fields.JSONField(null=True)  # type: ignore[var-annotated]

    @classmethod
    async def log_login_success(
        cls, user_id: uuid.UUID, ip_address: str, user_agent: str
    ) -> "UserEvent":
        """Log a successful login event.

        Args:
            user_id: The ID of the user who logged in.
            ip_address: The IP address of the client.
            user_agent: The user agent string of the client.

        Returns:
            The created event.
        """
        return await cls.create(
            user_id=user_id,
            event_type="login_success",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @classmethod
    async def log_login_failure(
        cls, user_id: uuid.UUID | None, ip_address: str, user_agent: str
    ) -> "UserEvent":
        """Log a failed login attempt.

        Args:
            user_id: The ID of the user who attempted to log in, if known.
            ip_address: The IP address of the client.
            user_agent: The user agent string of the client.

        Returns:
            The created event.
        """
        return await cls.create(
            user_id=user_id,
            event_type="login_failure",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @classmethod
    async def log_logout(
        cls, user_id: uuid.UUID, ip_address: str, user_agent: str
    ) -> "UserEvent":
        """Log a logout event.

        Args:
            user_id: The ID of the user who logged out.
            ip_address: The IP address of the client.
            user_agent: The user agent string of the client.

        Returns:
            The created event.
        """
        return await cls.create(
            user_id=user_id,
            event_type="logout",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @classmethod
    async def log_password_change(
        cls, user_id: uuid.UUID, ip_address: str, user_agent: str
    ) -> "UserEvent":
        """Log a password change event.

        Args:
            user_id: The ID of the user who changed their password.
            ip_address: The IP address of the client.
            user_agent: The user agent string of the client.

        Returns:
            The created event.
        """
        return await cls.create(
            user_id=user_id,
            event_type="password_change",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @classmethod
    async def log_account_lockout(
        cls, user_id: uuid.UUID, ip_address: str, user_agent: str
    ) -> "UserEvent":
        """Log an account lockout event.

        Args:
            user_id: The ID of the user whose account was locked.
            ip_address: The IP address of the client.
            user_agent: The user agent string of the client.

        Returns:
            The created event.
        """
        return await cls.create(
            user_id=user_id,
            event_type="account_lockout",
            ip_address=ip_address,
            user_agent=user_agent,
        )
