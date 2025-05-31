from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation

from backend.db.base import BaseModel
from backend.db.models.pending_post import PendingPost


class AIAnalysis(BaseModel):
    pending_post: ForeignKeyRelation[PendingPost] = fields.ForeignKeyField(
        "models.PendingPost",
        related_name="ai_analyses",
    )
    decision = fields.CharField(max_length=20)  # APPROVED or REJECTED
    confidence_score = fields.FloatField()
    analysis_text = fields.TextField()
    feedback_text = fields.TextField()
    processing_time_ms = fields.IntField()
