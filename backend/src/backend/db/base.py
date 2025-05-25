"""Base model for all database models."""

from typing import Any
from typing import Optional
import uuid

from tortoise import fields
from tortoise.models import Model

from backend.utils.datetime import now


class BaseModel(Model):
    """Base model for all database models.

    All models will inherit from this base model with common fields.
    """

    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        """Meta class for BaseModel."""

        abstract = True

    async def soft_delete(self) -> None:
        """Soft delete the model by setting deleted_at to current time."""
        self.deleted_at = now()
        await self.save()

    @classmethod
    async def get_or_none(cls, **kwargs: Any) -> Optional["BaseModel"]:
        """Get an object or return None if it doesn't exist.

        This method also excludes soft-deleted objects by default.
        """
        kwargs["deleted_at"] = None
        return await cls.filter(**kwargs).first()
