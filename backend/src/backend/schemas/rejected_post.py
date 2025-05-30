from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

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


class RejectedPostList(BaseModel):
    rejected_posts: List[RejectedPostResponse]
    count: int
