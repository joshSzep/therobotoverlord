from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from backend.schemas.user import UserSchema


class PostBase(BaseModel):
    content: str


class PostCreate(PostBase):
    topic_id: UUID
    parent_post_id: Optional[UUID] = None


class PostUpdate(BaseModel):
    content: str


class PostResponse(PostBase):
    id: UUID
    author: UserSchema
    topic_id: UUID
    parent_post_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    reply_count: int = 0
    replies: List["PostResponse"] = []


class PostList(BaseModel):
    posts: List[PostResponse]
    count: int
