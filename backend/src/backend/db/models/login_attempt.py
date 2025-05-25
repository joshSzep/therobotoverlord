"""Login attempt model for security monitoring."""

from tortoise import fields

from backend.db.base import BaseModel


class LoginAttempt(BaseModel):
    """Login attempt model for security monitoring."""

    user = fields.ForeignKeyField(  # type: ignore[var-annotated]
        "models.User",
        related_name="login_attempts",
        null=True,
    )
    ip_address = fields.CharField(max_length=45)
    user_agent = fields.CharField(max_length=255)
    success = fields.BooleanField()
    timestamp = fields.DatetimeField(auto_now_add=True)
