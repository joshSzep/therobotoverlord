# Export the main template functions for easy importing
# Auth templates
from backend.dominate_templates.auth.login import create_login_page
from backend.dominate_templates.auth.register import create_register_page
from backend.dominate_templates.base import create_base_document
from backend.dominate_templates.home import create_home_page

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
    "create_post_detail_page",
    "create_topic_detail_page",
    "create_topics_list_page",
    "create_profile_page",
]
