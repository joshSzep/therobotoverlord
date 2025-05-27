# Standard library imports
from datetime import timedelta
from typing import Any
from typing import List
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_event_to_schema
from backend.db.models.user_event import UserEvent
from backend.schemas.user_event import UserEventListSchema
from backend.schemas.user_event import UserEventSchema
from backend.utils.datetime import now_utc


class UserEventRepository:
    @staticmethod
    async def create_event(
        event_type: str,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> UserEventSchema:
        event = await UserEvent.create(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
        )
        return await user_event_to_schema(event)

    @staticmethod
    async def log_login_success(
        user_id: UUID,
        ip_address: str,
        user_agent: str,
    ) -> UserEventSchema:
        event = await UserEvent.create(
            user_id=user_id,
            event_type="login",
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"success": True},
        )
        return await user_event_to_schema(event)

    @staticmethod
    async def log_login_failure(
        user_id: Optional[UUID],
        ip_address: str,
        user_agent: str,
    ) -> UserEventSchema:
        event = await UserEvent.create(
            user_id=user_id,
            event_type="login",
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"success": False},
        )
        return await user_event_to_schema(event)

    @staticmethod
    async def log_logout(
        user_id: UUID,
        ip_address: str,
        user_agent: str,
    ) -> UserEventSchema:
        event = await UserEvent.log_logout(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await user_event_to_schema(event)

    @staticmethod
    async def log_password_change(
        user_id: UUID,
        ip_address: str,
        user_agent: str,
    ) -> UserEventSchema:
        event = await UserEvent.log_password_change(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await user_event_to_schema(event)

    @staticmethod
    async def log_account_lockout(
        user_id: UUID,
        ip_address: str,
        user_agent: str,
    ) -> UserEventSchema:
        event = await UserEvent.log_account_lockout(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await user_event_to_schema(event)

    @staticmethod
    async def get_user_events(
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        event_type: Optional[str] = None,
    ) -> UserEventListSchema:
        query = UserEvent.filter(user_id=user_id)

        if event_type:
            query = query.filter(event_type=event_type)

        # Get total count for pagination
        count = await query.count()

        # Apply pagination
        events = await query.offset(skip).limit(limit).order_by("-created_at")

        # Convert ORM models to schema objects using async converter
        event_schemas: list[UserEventSchema] = []
        for event in events:
            event_schemas.append(await user_event_to_schema(event))

        return UserEventListSchema(events=event_schemas, count=count)

    @staticmethod
    async def create_login_attempt(
        user_id: Optional[UUID],
        ip_address: str,
        user_agent: str,
        success: bool,
    ) -> UserEventSchema:
        # Create a user event with login information
        event = await UserEvent.create(
            user_id=user_id,
            event_type="login",
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"success": success},
        )
        return await user_event_to_schema(event)

    @staticmethod
    async def get_recent_login_attempts(
        user_id: UUID,
        limit: int = 10,
    ) -> List[UserEventSchema]:
        events = (
            await UserEvent.filter(
                user_id=user_id,
                event_type="login",
            )
            .order_by("-created_at")
            .limit(limit)
        )

        # Convert ORM models to schema objects using async converter
        event_schemas: list[UserEventSchema] = []
        for event in events:
            event_schemas.append(await user_event_to_schema(event))

        return event_schemas

    @staticmethod
    async def get_recent_failed_login_attempts(
        user_id: UUID,
        hours: int = 24,
        limit: int = 10,
    ) -> List[UserEventSchema]:
        time_threshold = now_utc() - timedelta(hours=hours)

        events = (
            await UserEvent.filter(
                user_id=user_id,
                event_type="login",
                created_at__gte=time_threshold,
            )
            .filter(metadata__contains={"success": False})
            .order_by("-created_at")
            .limit(limit)
        )

        # Convert ORM models to schema objects using async converter
        event_schemas: list[UserEventSchema] = []
        for event in events:
            event_schemas.append(await user_event_to_schema(event))

        return event_schemas

    @staticmethod
    async def count_recent_failed_login_attempts(
        user_id: UUID,
        hours: int = 24,
    ) -> int:
        time_threshold = now_utc() - timedelta(hours=hours)

        return (
            await UserEvent.filter(
                user_id=user_id,
                event_type="login",
                created_at__gte=time_threshold,
            )
            .filter(metadata__contains={"success": False})
            .count()
        )

    @staticmethod
    async def list_login_attempts(
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        success: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> UserEventListSchema:
        query = UserEvent.filter(event_type="login")

        if user_id:
            query = query.filter(user_id=user_id)

        if ip_address:
            query = query.filter(ip_address=ip_address)

        if success is not None:
            query = query.filter(metadata__contains={"success": success})

        # Get total count for pagination
        count = await query.count()

        # Apply pagination
        attempts = await query.offset(skip).limit(limit).order_by("-created_at")

        # Convert ORM models to schema objects using async converter
        event_schemas: list[UserEventSchema] = []
        for attempt in attempts:
            event_schemas.append(await user_event_to_schema(attempt))

        return UserEventListSchema(events=event_schemas, count=count)
