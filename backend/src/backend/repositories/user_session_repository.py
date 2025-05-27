# Standard library imports
from datetime import timedelta
import secrets
from typing import List
from typing import Optional
from typing import Tuple
from uuid import UUID

# Project-specific imports
from backend.converters import user_session_to_schema
from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSessionSchema
from backend.utils.datetime import now_utc


class UserSessionRepository:
    @staticmethod
    async def create_session(
        user_id: UUID,
        ip_address: str,
        user_agent: str,
        expires_in_days: int = 7,
    ) -> UserSessionSchema:
        session_token = secrets.token_hex(32)

        session = await UserSession.create(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_token=session_token,
            is_active=True,
            expires_at=now_utc() + timedelta(days=expires_in_days),
        )

        return await user_session_to_schema(session)

    @staticmethod
    async def get_session_by_token(session_token: str) -> Optional[UserSessionSchema]:
        session = await UserSession.get_or_none(
            session_token=session_token,
            is_active=True,
        ).prefetch_related("user")

        if session:
            return await user_session_to_schema(session)
        return None

    @staticmethod
    async def validate_session(session_token: str) -> Optional[UserSessionSchema]:
        # Get the raw session model first to check expiration and update if needed
        session = await UserSession.get_or_none(
            session_token=session_token,
            is_active=True,
        ).prefetch_related("user")

        if not session:
            return None

        # Check if session is expired
        if session.expires_at < now_utc():
            session.is_active = False
            await session.save()
            return None

        return await user_session_to_schema(session)

    @staticmethod
    async def deactivate_session(session_token: str) -> bool:
        session = await UserSession.get_or_none(session_token=session_token)
        if not session:
            return False

        session.is_active = False
        await session.save()
        return True

    @staticmethod
    async def deactivate_all_user_sessions(user_id: UUID) -> int:
        sessions = await UserSession.filter(user_id=user_id, is_active=True)
        count = 0

        for session in sessions:
            session.is_active = False
            await session.save()
            count += 1

        return count

    @staticmethod
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

    @staticmethod
    async def cleanup_expired_sessions() -> int:
        """Deactivate all expired sessions."""
        current_time = now_utc()
        sessions = await UserSession.filter(is_active=True, expires_at__lt=current_time)
        count = 0

        for session in sessions:
            session.is_active = False
            await session.save()
            count += 1

        return count
