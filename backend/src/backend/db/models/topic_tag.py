from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation

from backend.db.base import BaseModel

if TYPE_CHECKING:
    from backend.db.models.tag import Tag
    from backend.db.models.topic import Topic


class TopicTag(BaseModel):
    class Meta:  # type: ignore[reportIncompatibleVariableOverride, unused-ignore]
        table = "topic_tag"
        unique_together = (("topic", "tag"),)

    topic: ForeignKeyRelation["Topic"] = fields.ForeignKeyField(
        "models.Topic",
        related_name="topic_tags",
    )
    tag: ForeignKeyRelation["Tag"] = fields.ForeignKeyField(
        "models.Tag",
        related_name="topic_tags",
    )
