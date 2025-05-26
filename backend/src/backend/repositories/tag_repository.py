# Standard library imports
from typing import List
from typing import Optional
from typing import Tuple

# Project-specific imports
from backend.db.models.tag import Tag


class TagRepository:
    @staticmethod
    async def list_tags(
        skip: int = 0, limit: int = 50, search: Optional[str] = None
    ) -> Tuple[List[Tag], int]:
        query = Tag.all()

        if search:
            query = query.filter(name__icontains=search)

        # Get total count for pagination
        count = await query.count()

        # Apply pagination
        tags = await query.offset(skip).limit(limit)

        return tags, count

    @staticmethod
    async def get_tag_by_id(tag_id: str) -> Optional[Tag]:
        return await Tag.get_or_none(id=tag_id)

    @staticmethod
    async def get_tag_by_slug(slug: str) -> Optional[Tag]:
        return await Tag.get_or_none(slug=slug)

    @staticmethod
    async def create_tag(name: str, slug: str) -> Tag:
        return await Tag.create(name=name, slug=slug)

    @staticmethod
    async def update_tag(tag_id: str, name: str, slug: str) -> Optional[Tag]:
        tag = await Tag.get_or_none(id=tag_id)
        if tag:
            tag.name = name
            tag.slug = slug
            await tag.save()
        return tag

    @staticmethod
    async def delete_tag(tag_id: str) -> bool:
        tag = await Tag.get_or_none(id=tag_id)
        if tag:
            await tag.delete()
            return True
        return False
