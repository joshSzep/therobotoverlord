from datetime import datetime
import uuid

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class UserSchema(BaseModel):
    id: uuid.UUID
    email: EmailStr
    display_name: str
    is_verified: bool
    last_login: datetime | None = None
    role: str
    is_locked: bool = False
    created_at: datetime
    updated_at: datetime
    approved_count: int = 0
    rejected_count: int = 0


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: str = Field(..., min_length=3, max_length=100)


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserSessionSchema(BaseModel):
    id: uuid.UUID
    ip_address: str
    user_agent: str
    session_token: str
    expires_at: datetime
    is_active: bool
    created_at: datetime
    user_id: uuid.UUID
