from tortoise import fields

from backend.db.base import BaseModel


class LoginAttempt(BaseModel):
    """Login attempt model for security monitoring.

    Attributes:
        user (User): The user associated with the login attempt. Returns None if the
            user does not exist.

        ip_address (str): The IP address of the client.
        user_agent (str): The user agent of the client.
        success (bool): Whether the login attempt was successful.
        timestamp (datetime): The timestamp of the login attempt.

    """

    user = fields.ForeignKeyField(  # type: ignore[var-annotated]
        "models.User",
        related_name="login_attempts",
        null=True,
    )
    ip_address = fields.CharField(max_length=45)
    user_agent = fields.CharField(max_length=255)
    success = fields.BooleanField()
    timestamp = fields.DatetimeField(auto_now_add=True)
