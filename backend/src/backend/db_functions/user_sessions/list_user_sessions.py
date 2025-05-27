# Standard library imports
from typing import List
from typing import Tuple
from uuid import UUID

# Project-specific imports
from backend.converters import user_session_to_schema
from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSessionSchema


async def list_user_sessions(
    user_id: UUID,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[UserSessionSchema], int]:
    query = UserSession.filter(user_id=user_id)

    if active_only:
        query = query.filter(is_active=True)

    # Get total count for pagination
    count = await query.count()

    # Apply pagination
    sessions = await query.offset(skip).limit(limit).order_by("-created_at")

    # Convert ORM models to schema objects using async converter
    session_schemas: List[UserSessionSchema] = []
    for session in sessions:
        session_schemas.append(await user_session_to_schema(session))

    return session_schemas, count
