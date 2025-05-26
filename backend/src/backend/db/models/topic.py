from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation

from backend.db.base import BaseModel
from backend.db.models.user import User

if TYPE_CHECKING:
    from backend.db.models.post import Post
    from backend.db.models.topic_tag import TopicTag


class Topic(BaseModel):
    topic_tags: fields.ReverseRelation["TopicTag"]
    posts: fields.ReverseRelation["Post"]

    title = fields.CharField(
        max_length=255,
    )
    author: ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="topics",
    )
    description = fields.TextField(
        null=True,
    )
