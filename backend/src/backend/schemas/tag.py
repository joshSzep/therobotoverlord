from typing import List
from uuid import UUID

from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
    slug: str


class TagCreate(BaseModel):
    name: str


class TagResponse(TagBase):
    id: UUID


class TagList(BaseModel):
    tags: List[TagResponse]
    count: int
