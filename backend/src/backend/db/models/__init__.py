from backend.db.models.login_attempt import LoginAttempt
from backend.db.models.post import Post
from backend.db.models.tag import Tag
from backend.db.models.topic import Topic
from backend.db.models.topic_tag import TopicTag
from backend.db.models.user import User
from backend.db.models.user import UserRole
from backend.db.models.user_event import UserEvent
from backend.db.models.user_session import UserSession

# This list is used for Tortoise ORM registration
models = [
    User,
    UserSession,
    LoginAttempt,
    UserEvent,
    Topic,
    Tag,
    TopicTag,
    Post,
]

__all__ = [
    "User",
    "UserRole",
    "UserSession",
    "LoginAttempt",
    "UserEvent",
    "Topic",
    "Tag",
    "TopicTag",
    "Post",
]
