"""
Topic-related data access functions.

This module provides functions for working with topics in the database.
"""

from backend.db_functions.topics.create_topic import create_topic
from backend.db_functions.topics.delete_topic import delete_topic
from backend.db_functions.topics.get_topic_by_id import get_topic_by_id
from backend.db_functions.topics.is_user_topic_author import is_user_topic_author
from backend.db_functions.topics.list_topics import list_topics
from backend.db_functions.topics.update_topic import update_topic

__all__ = [
    "create_topic",
    "delete_topic",
    "get_topic_by_id",
    "is_user_topic_author",
    "list_topics",
    "update_topic",
]
