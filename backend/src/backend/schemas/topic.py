# Standard library imports
from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

# Third-party imports
from pydantic import BaseModel
from pydantic import Field

# Project-specific imports
from backend.schemas.tag import TagResponse
from backend.schemas.user import UserSchema


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
