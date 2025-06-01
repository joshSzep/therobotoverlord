from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class AdminUserCreate(BaseModel):
    email: EmailStr
    display_name: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    secret_key: str
