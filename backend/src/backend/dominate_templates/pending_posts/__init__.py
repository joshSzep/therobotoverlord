"""
Pending posts templates for The Robot Overlord.
"""

from backend.dominate_templates.pending_posts.detail import (
    create_pending_post_detail_page,
)
from backend.dominate_templates.pending_posts.list import create_pending_posts_list_page

__all__ = [
    "create_pending_post_detail_page",
    "create_pending_posts_list_page",
]
