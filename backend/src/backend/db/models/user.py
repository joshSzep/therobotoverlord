"""User model for authentication and user management."""

from datetime import timedelta
import enum

import bcrypt
from tortoise import fields

from backend.db.base import BaseModel
from backend.utils.datetime import now


class UserRole(str, enum.Enum):
    """User role enum."""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(BaseModel):
    """User model with authentication fields."""

    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    display_name = fields.CharField(max_length=100)
    is_verified = fields.BooleanField(default=False)
    verification_token = fields.CharField(max_length=255, null=True)
    last_login = fields.DatetimeField(null=True)
    failed_login_attempts = fields.IntField(default=0)
    role = fields.CharEnumField(UserRole, default=UserRole.USER)
    is_locked = fields.BooleanField(default=False)

    async def set_password(self, password: str) -> None:
        """Hash and set user password."""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed.decode("utf-8")

    async def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        password_bytes = password.encode("utf-8")
        hash_bytes = self.password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)

    async def record_login_success(self, ip_address: str, user_agent: str) -> None:
        """Record a successful login attempt.

        Args:
            ip_address: The IP address of the client.
            user_agent: The user agent of the client.
        """
        # Update user fields
        self.last_login = now()
        self.failed_login_attempts = 0
        self.is_locked = False
        await self.save()

        # Generate a session token
        import secrets

        session_token = secrets.token_hex(32)

        # Create a session record
        from backend.db.models.user_session import UserSession

        await UserSession.create(
            user=self,
            ip_address=ip_address,
            user_agent=user_agent,
            session_token=session_token,
            is_active=True,
            expires_at=now() + timedelta(days=7),
        )

        # Record the login attempt
        from backend.db.models.login_attempt import LoginAttempt

        await LoginAttempt.create(
            user=self,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
        )

    async def record_login_failure(self, ip_address: str, user_agent: str) -> None:
        """Record failed login attempt and lock account if needed."""
        self.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        was_locked = False
        if self.failed_login_attempts >= 5 and not self.is_locked:
            self.is_locked = True
            was_locked = True

        await self.save()

        # Record the login attempt
        from backend.db.models.login_attempt import LoginAttempt

        await LoginAttempt.create(
            user=self,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
        )

        # Log account lockout event if account was just locked
        if was_locked:
            # Import here to avoid circular import
            from backend.db.models.user_event import UserEvent

            await UserEvent.log_account_lockout(self.id, ip_address, user_agent)
