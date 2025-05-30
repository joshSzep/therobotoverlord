from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation

from backend.db.base import BaseModel
from backend.db.models.user import User

if TYPE_CHECKING:
    from backend.db.models.topic import Topic


class PendingPost(BaseModel):
    content = fields.TextField()
    author: ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="pending_posts",
    )
    topic: ForeignKeyRelation["Topic"] = fields.ForeignKeyField(
        "models.Topic",
        related_name="pending_posts",
    )
    parent_post_id = fields.UUIDField(null=True)
