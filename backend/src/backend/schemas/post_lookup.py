"""
Schemas for the post lookup system.
"""

from enum import Enum
from typing import Generic
from typing import Optional
from typing import TypeVar
from typing import Union
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from backend.schemas.pending_post import PendingPostResponse
from backend.schemas.post import PostResponse
from backend.schemas.rejected_post import RejectedPostResponse

# Define a type variable for the post types
PostT = TypeVar("PostT", PostResponse, PendingPostResponse, RejectedPostResponse)


class PostType(str, Enum):
    """Enum for post types."""

    APPROVED = "approved"
    PENDING = "pending"
    REJECTED = "rejected"


class PostLookupResult(BaseModel, Generic[PostT]):
    """
    Result of a post lookup operation.

    Generic over the post type to allow for different post schemas.
    """

    type: PostType
    post: PostT
    visible_to_user: bool = True


class ThreadPost(BaseModel):
    """
    A post in a thread structure, which can be an approved, pending, or rejected post.

    This model provides a unified interface for all post types in thread structures.
    """

    id: UUID
    content: str
    author_id: UUID
    parent_post_id: Optional[UUID] = None
    replies: list["ThreadPost"] = Field(default_factory=list)
    post_type: PostType
    original_post: Union[PostResponse, PendingPostResponse, RejectedPostResponse]
