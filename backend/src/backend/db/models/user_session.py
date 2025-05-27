from tortoise import fields

from backend.db.base import BaseModel


class UserSession(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="sessions")  # type: ignore[var-annotated]
    ip_address = fields.CharField(max_length=45)  # IPv6 can be up to 45 chars
    user_agent = fields.CharField(max_length=255)
    session_token = fields.CharField(max_length=255)
    expires_at = fields.DatetimeField()
    is_active = fields.BooleanField(default=True)
