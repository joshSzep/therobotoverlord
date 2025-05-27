"""
Topic-Tag relationship data access functions.

This module provides functions for working with topic-tag relationships in the database.
"""

from backend.db_functions.topic_tags.add_tags_to_topic import add_tags_to_topic
from backend.db_functions.topic_tags.create_topic_tag import create_topic_tag
from backend.db_functions.topic_tags.delete_topic_tag import delete_topic_tag
from backend.db_functions.topic_tags.get_tags_for_topic import get_tags_for_topic
from backend.db_functions.topic_tags.get_topic_tag import get_topic_tag
from backend.db_functions.topic_tags.get_topics_for_tag import get_topics_for_tag
from backend.db_functions.topic_tags.remove_tags_from_topic import (
    remove_tags_from_topic,
)
from backend.db_functions.topic_tags.set_topic_tags import set_topic_tags

__all__ = [
    "add_tags_to_topic",
    "create_topic_tag",
    "delete_topic_tag",
    "get_tags_for_topic",
    "get_topic_tag",
    "get_topics_for_tag",
    "remove_tags_from_topic",
    "set_topic_tags",
]
