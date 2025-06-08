from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from backend.schemas.user import UserSchema


class RejectedPostBase(BaseModel):
    content: str


class RejectedPostResponse(RejectedPostBase):
    id: UUID
    author: UserSchema
    topic_id: UUID
    parent_post_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    moderation_reason: str
    topic: Optional[Dict[str, Any]] = None


class RejectedPostList(BaseModel):
    rejected_posts: List[RejectedPostResponse]
    count: int


class RejectionRequest(BaseModel):
    reason: str = Field(
        ...,
        min_length=3,
        max_length=1024,
        description="Reason for rejecting the post",
    )
