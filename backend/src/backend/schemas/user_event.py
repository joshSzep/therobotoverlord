# Standard library imports
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import uuid

# Third-party imports
from pydantic import BaseModel


class UserEventSchema(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    event_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[uuid.UUID] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class UserEventResponse(UserEventSchema):
    # This class inherits all fields from UserEventSchema
    # We can override or add specific fields as needed
    pass


class UserEventListSchema(BaseModel):
    user_events: List[UserEventSchema]
    count: int
