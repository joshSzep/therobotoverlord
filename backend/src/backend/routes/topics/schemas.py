from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from backend.routes.users.users_schemas import UserSchema


class TagBase(BaseModel):
    name: str
    slug: str


class TagResponse(TagBase):
    id: UUID

    class Config:
        from_attributes = True


class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None


class TopicCreate(TopicBase):
    tags: List[str] = Field(default_factory=list)


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class TopicResponse(TopicBase):
    id: UUID
    author: UserSchema
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class TopicList(BaseModel):
    topics: List[TopicResponse]
    count: int
