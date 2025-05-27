from pydantic import BaseModel


class PasswordChangeRequestSchema(BaseModel):
    current_password: str
    new_password: str
