# Standard library imports
from datetime import datetime
from typing import Optional
import uuid

# Third-party imports
from pydantic import BaseModel
from pydantic import EmailStr


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    display_name: str
    is_verified: bool
    last_login: Optional[datetime] = None
    role: str
    is_locked: bool = False
    created_at: datetime
    updated_at: datetime

    # Additional fields for templates
    approved_count: int = 0
    rejected_count: int = 0

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def display_email(self) -> str:
        return self.email.upper()
