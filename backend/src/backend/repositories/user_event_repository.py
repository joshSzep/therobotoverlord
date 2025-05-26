# Standard library imports
from typing import List
from typing import Optional
from typing import Tuple
from uuid import UUID

# Project-specific imports
from backend.db.models.user_event import UserEvent


class UserEventRepository:
    @staticmethod
    async def create_event(
        event_type: str,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> UserEvent:
        return await UserEvent.create(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
        )

    @staticmethod
    async def log_login_success(
        user_id: UUID,
        ip_address: str,
        user_agent: str,
    ) -> UserEvent:
        return await UserEvent.log_login_success(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    async def log_login_failure(
        user_id: Optional[UUID],
        ip_address: str,
        user_agent: str,
    ) -> UserEvent:
        return await UserEvent.log_login_failure(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    async def log_logout(
        user_id: UUID,
        ip_address: str,
        user_agent: str,
    ) -> UserEvent:
        return await UserEvent.log_logout(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    async def log_password_change(
        user_id: UUID,
        ip_address: str,
        user_agent: str,
    ) -> UserEvent:
        return await UserEvent.log_password_change(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    async def log_account_lockout(
        user_id: UUID,
        ip_address: str,
        user_agent: str,
    ) -> UserEvent:
        return await UserEvent.log_account_lockout(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    async def get_user_events(
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        event_type: Optional[str] = None,
    ) -> Tuple[List[UserEvent], int]:
        query = UserEvent.filter(user_id=user_id)

        if event_type:
            query = query.filter(event_type=event_type)

        # Get total count for pagination
        count = await query.count()

        # Apply pagination
        events = await query.offset(skip).limit(limit).order_by("-created_at")

        return events, count
