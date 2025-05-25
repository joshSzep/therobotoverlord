from tortoise import fields

from backend.db.base import BaseModel
from backend.utils.datetime import now_utc


class UserSession(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="sessions")  # type: ignore[var-annotated]
    ip_address = fields.CharField(max_length=45)  # IPv6 can be up to 45 chars
    user_agent = fields.CharField(max_length=255)
    session_token = fields.CharField(max_length=255)
    expires_at = fields.DatetimeField()
    is_active = fields.BooleanField(default=True)

    async def invalidate(self) -> None:
        self.is_active = False
        await self.save()

    @classmethod
    async def cleanup_expired(cls) -> int:
        count = await cls.filter(
            expires_at__lt=now_utc(),
            is_active=True,
        ).update(is_active=False)
        return count
