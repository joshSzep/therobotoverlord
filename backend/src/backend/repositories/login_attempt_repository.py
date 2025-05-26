# Standard library imports
from datetime import timedelta
from typing import List
from typing import Optional
from typing import Tuple
from uuid import UUID

# Project-specific imports
from backend.db.models.login_attempt import LoginAttempt
from backend.utils.datetime import now_utc


class LoginAttemptRepository:
    @staticmethod
    async def create_login_attempt(
        user_id: Optional[UUID],
        ip_address: str,
        user_agent: str,
        success: bool,
    ) -> LoginAttempt:
        return await LoginAttempt.create(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
        )

    @staticmethod
    async def get_recent_login_attempts(
        user_id: UUID,
        limit: int = 10,
    ) -> List[LoginAttempt]:
        return (
            await LoginAttempt.filter(user_id=user_id)
            .order_by("-created_at")
            .limit(limit)
        )

    @staticmethod
    async def get_recent_failed_attempts(
        user_id: UUID,
        hours: int = 24,
        limit: int = 10,
    ) -> List[LoginAttempt]:
        time_threshold = now_utc() - timedelta(hours=hours)

        return (
            await LoginAttempt.filter(
                user_id=user_id,
                success=False,
                created_at__gte=time_threshold,
            )
            .order_by("-created_at")
            .limit(limit)
        )

    @staticmethod
    async def count_recent_failed_attempts(
        user_id: UUID,
        hours: int = 24,
    ) -> int:
        time_threshold = now_utc() - timedelta(hours=hours)

        return await LoginAttempt.filter(
            user_id=user_id,
            success=False,
            created_at__gte=time_threshold,
        ).count()

    @staticmethod
    async def list_login_attempts(
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        success: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[LoginAttempt], int]:
        query = LoginAttempt.all()

        if user_id:
            query = query.filter(user_id=user_id)

        if ip_address:
            query = query.filter(ip_address=ip_address)

        if success is not None:
            query = query.filter(success=success)

        # Get total count for pagination
        count = await query.count()

        # Apply pagination
        attempts = await query.offset(skip).limit(limit).order_by("-created_at")

        return attempts, count
