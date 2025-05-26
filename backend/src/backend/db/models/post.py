from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.fields.relational import ForeignKeyNullableRelation
from tortoise.fields.relational import ForeignKeyRelation

from backend.db.base import BaseModel
from backend.db.models.user import User

if TYPE_CHECKING:
    from backend.db.models.topic import Topic


class Post(BaseModel):
    # This type hint is for IDE support only
    replies = fields.ReverseRelation["Post"]

    content = fields.TextField()
    author: ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="posts",
    )
    topic: ForeignKeyRelation["Topic"] = fields.ForeignKeyField(
        "models.Topic",
        related_name="posts",
    )
    parent_post: ForeignKeyNullableRelation["Post"] = fields.ForeignKeyField(
        "models.Post",
        related_name="replies",
        null=True,
    )
