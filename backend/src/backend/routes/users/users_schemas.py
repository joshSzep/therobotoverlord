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
    created_at: datetime
    updated_at: datetime


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: str = Field(..., min_length=3, max_length=100)


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


class UserSessionSchema(BaseModel):
    id: uuid.UUID
    ip_address: str
    user_agent: str
    expires_at: datetime
    is_active: bool
    created_at: datetime


class LoginAttemptSchema(BaseModel):
    id: uuid.UUID
    ip_address: str
    user_agent: str
    success: bool
    timestamp: datetime


class PasswordChangeRequestSchema(BaseModel):
    current_password: str
    new_password: str
