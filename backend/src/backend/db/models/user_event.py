from tortoise import fields

from backend.db.base import BaseModel


class UserEvent(BaseModel):
    user = fields.ForeignKeyField(  # type: ignore[var-annotated]
        "models.User",
        related_name="events",
        null=True,
    )
    event_type = fields.CharField(
        max_length=50,
    )
    ip_address = fields.CharField(
        max_length=45,
        null=True,
    )
    user_agent = fields.CharField(
        max_length=255,
        null=True,
    )
    resource_type = fields.CharField(
        max_length=50,
        null=True,
    )
    resource_id = fields.UUIDField(
        null=True,
    )
    metadata = fields.JSONField(
        null=True,
    )  # type: ignore[var-annotated]
