from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from slugify import slugify
from tortoise.exceptions import DoesNotExist
from tortoise.exceptions import IntegrityError

from backend.db.models.tag import Tag
from backend.db.models.user import User
from backend.routes.tags.schemas import TagCreate
from backend.routes.tags.schemas import TagList
from backend.routes.tags.schemas import TagResponse
from backend.utils.auth import get_current_user

router = APIRouter(tags=["tags"])


@router.get("/", response_model=TagList)
async def list_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
) -> TagList:
    query = Tag.all()

    if search:
        # Filter by name if search parameter is provided
        query = query.filter(name__icontains=search)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    tags = await query.offset(skip).limit(limit)

    # Convert to response model
    tag_responses = [TagResponse.model_validate(tag) for tag in tags]

    return TagList(tags=tag_responses, count=count)


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate, current_user: User = Depends(get_current_user)
) -> TagResponse:
    # Only allow moderators or admins to create tags
    if current_user.role not in ["moderator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators and admins can create tags",
        )

    try:
        # Create the tag
        tag = await Tag.create(
            name=tag_data.name,
            slug=slugify(tag_data.name),
        )
        return TagResponse.model_validate(tag)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A tag with this name already exists",
        )


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: UUID) -> TagResponse:
    try:
        tag = await Tag.get(id=tag_id)
        return TagResponse.model_validate(tag)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
) -> TagResponse:
    # Only allow moderators or admins to update tags
    if current_user.role not in ["moderator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators and admins can update tags",
        )

    try:
        tag = await Tag.get(id=tag_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    try:
        # Update the tag
        tag.name = tag_data.name
        tag.slug = slugify(tag_data.name)
        await tag.save()
        return TagResponse.model_validate(tag)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A tag with this name already exists",
        )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    # Only allow admins to delete tags
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete tags",
        )

    try:
        tag = await Tag.get(id=tag_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    # Check if the tag is used by any topics
    tag_count = await tag.topic_tags.all().count()
    if tag_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete tag as it is used by {tag_count} topics",
        )

    # Delete the tag
    await tag.delete()
