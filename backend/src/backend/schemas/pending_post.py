from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from backend.schemas.user import UserSchema


class PendingPostBase(BaseModel):
    content: str


class PendingPostCreate(PendingPostBase):
    topic_id: UUID
    parent_post_id: Optional[UUID] = None


class PendingPostResponse(PendingPostBase):
    id: UUID
    author: UserSchema
    topic_id: UUID
    parent_post_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class PendingPostList(BaseModel):
    pending_posts: List[PendingPostResponse]
    count: int
