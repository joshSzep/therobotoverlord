# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import tag_to_schema
from backend.db.models.tag import Tag
from backend.schemas.tag import TagList
from backend.schemas.tag import TagResponse


class TagRepository:
    @staticmethod
    async def list_tags(
        skip: int = 0, limit: int = 50, search: Optional[str] = None
    ) -> TagList:
        query = Tag.all()

        if search:
            query = query.filter(name__icontains=search)

        # Get total count for pagination
        count = await query.count()

        # Apply pagination
        tags = await query.offset(skip).limit(limit)

        # Convert ORM models to schema objects using async converter
        tag_responses: list[TagResponse] = []
        for tag in tags:
            tag_responses.append(await tag_to_schema(tag))

        return TagList(tags=tag_responses, count=count)

    @staticmethod
    async def get_tag_by_id(tag_id: UUID) -> Optional[TagResponse]:
        tag = await Tag.get_or_none(id=tag_id)
        if tag:
            return await tag_to_schema(tag)
        return None

    @staticmethod
    async def get_tag_by_slug(slug: str) -> Optional[TagResponse]:
        tag = await Tag.get_or_none(slug=slug)
        if tag:
            return await tag_to_schema(tag)
        return None

    @staticmethod
    async def get_tag_by_name(name: str) -> Optional[TagResponse]:
        tag = await Tag.get_or_none(name=name)
        if tag:
            return await tag_to_schema(tag)
        return None

    @staticmethod
    async def create_tag(name: str, slug: str) -> TagResponse:
        tag = await Tag.create(name=name, slug=slug)
        return await tag_to_schema(tag)

    @staticmethod
    async def update_tag(tag_id: UUID, name: str, slug: str) -> Optional[TagResponse]:
        tag = await Tag.get_or_none(id=tag_id)
        if tag:
            tag.name = name
            tag.slug = slug
            await tag.save()
            return await tag_to_schema(tag)
        return None

    @staticmethod
    async def delete_tag(tag_id: UUID) -> bool:
        tag = await Tag.get_or_none(id=tag_id)
        if tag:
            await tag.delete()
            return True
        return False
