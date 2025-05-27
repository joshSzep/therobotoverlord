import enum

from tortoise import fields

from backend.db.base import BaseModel
from backend.db.models.user_session import UserSession


class UserRole(str, enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(BaseModel):
    sessions: fields.ReverseRelation[UserSession]

    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    display_name = fields.CharField(max_length=100)
    is_verified = fields.BooleanField(default=False)
    verification_token = fields.CharField(max_length=255, null=True)
    last_login = fields.DatetimeField(null=True)
    failed_login_attempts = fields.IntField(default=0)
    role = fields.CharEnumField(UserRole, default=UserRole.USER)
    is_locked = fields.BooleanField(default=False)
