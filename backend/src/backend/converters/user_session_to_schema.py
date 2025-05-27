from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSessionSchema


async def user_session_to_schema(session: UserSession) -> UserSessionSchema:
    return UserSessionSchema(
        id=session.id,
        ip_address=session.ip_address,
        user_agent=session.user_agent,
        session_token=session.session_token,
        expires_at=session.expires_at,
        is_active=session.is_active,
        created_at=session.created_at,
    )
