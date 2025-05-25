from uuid import uuid4

from tortoise import fields
from tortoise.models import Model

from backend.utils.datetime import now_utc


class BaseModel(Model):
    """Base model for all database models.

    All models will inherit from this base model with common fields.
    """

    id = fields.UUIDField(pk=True, default=uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride, unused-ignore]
        abstract = True

    async def soft_delete(self) -> None:
        """Soft delete the model by setting deleted_at to current time."""
        self.deleted_at = now_utc()
        await self.save()

    async def is_soft_deleted(self) -> bool:
        """Check if the model is soft deleted."""
        return self.deleted_at is not None  # type: ignore[reportUnnecessaryComparison, unused-ignore]
