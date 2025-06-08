# Export the main template functions for easy importing

# Auth templates
from backend.dominate_templates.auth.login import create_login_page
from backend.dominate_templates.auth.register import create_register_page

# Base template
from backend.dominate_templates.base import create_base_document

# Home template
from backend.dominate_templates.home import create_home_page

# Pending posts templates
from backend.dominate_templates.pending_posts.detail import (
    create_pending_post_detail_page,
)
from backend.dominate_templates.pending_posts.list import create_pending_posts_list_page

# Posts templates
from backend.dominate_templates.posts.detail import create_post_detail_page

# Profile templates
from backend.dominate_templates.profile.index import create_profile_page

# Topics templates
from backend.dominate_templates.topics.detail import create_topic_detail_page
from backend.dominate_templates.topics.list import create_topics_list_page

# Define what's exported from this module
__all__ = [
    "create_base_document",
    "create_home_page",
    "create_login_page",
    "create_register_page",
    "create_pending_posts_list_page",
    "create_pending_post_detail_page",
    "create_post_detail_page",
    "create_topic_detail_page",
    "create_topics_list_page",
    "create_profile_page",
]
