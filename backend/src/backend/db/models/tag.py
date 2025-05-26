from typing import TYPE_CHECKING

from tortoise import fields

from backend.db.base import BaseModel

if TYPE_CHECKING:
    from backend.db.models.topic_tag import TopicTag


class Tag(BaseModel):
    topic_tags: fields.ReverseRelation["TopicTag"]

    name = fields.CharField(max_length=50, unique=True)
    slug = fields.CharField(max_length=50, unique=True)
