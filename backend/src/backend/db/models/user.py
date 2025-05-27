import enum

import bcrypt
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

    async def set_password(self, password: str) -> None:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed.decode("utf-8")

    async def verify_password(self, password: str) -> bool:
        password_bytes = password.encode("utf-8")
        hash_bytes = self.password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
