from uuid import UUID

from pydantic import BaseModel


class UserStatsResponse(BaseModel):
    user_id: UUID
    username: str
    approved_count: int
    rejected_count: int
    pending_count: int
    approval_rate: float  # Percentage of approved posts out of total decisions
