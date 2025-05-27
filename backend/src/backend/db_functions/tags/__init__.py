"""
Tag-related data access functions.

This module provides functions for working with tags in the database.
"""

from backend.db_functions.tags.create_tag import create_tag
from backend.db_functions.tags.delete_tag import delete_tag
from backend.db_functions.tags.get_tag_by_id import get_tag_by_id
from backend.db_functions.tags.get_tag_by_name import get_tag_by_name
from backend.db_functions.tags.get_tag_by_slug import get_tag_by_slug
from backend.db_functions.tags.list_tags import list_tags
from backend.db_functions.tags.update_tag import update_tag

__all__ = [
    "create_tag",
    "delete_tag",
    "get_tag_by_id",
    "get_tag_by_name",
    "get_tag_by_slug",
    "list_tags",
    "update_tag",
]
