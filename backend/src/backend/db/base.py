from uuid import uuid4

from tortoise import fields
from tortoise.models import Model


class BaseModel(Model):
    class Meta:  # type: ignore[reportIncompatibleVariableOverride, unused-ignore]
        abstract = True

    id = fields.UUIDField(pk=True, default=uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
