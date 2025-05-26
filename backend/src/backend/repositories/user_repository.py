# Standard library imports
from typing import List
from typing import Optional
from typing import Tuple
from uuid import UUID

# Project-specific imports
from backend.db.models.user import User


class UserRepository:
    @staticmethod
    async def get_user_by_id(user_id: UUID) -> Optional[User]:
        return await User.get_or_none(id=user_id)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        return await User.get_or_none(email=email)

    @staticmethod
    async def create_user(email: str, password: str, display_name: str) -> User:
        user = await User.create(
            email=email,
            password_hash="",  # Temporary placeholder
            display_name=display_name,
        )
        await user.set_password(password)
        await user.save()
        return user

    @staticmethod
    async def update_user(
        user_id: UUID,
        display_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[User]:
        user = await User.get_or_none(id=user_id)
        if not user:
            return None

        if display_name:
            user.display_name = display_name

        if email:
            user.email = email

        await user.save()
        return user

    @staticmethod
    async def set_user_password(user_id: UUID, password: str) -> Optional[User]:
        user = await User.get_or_none(id=user_id)
        if not user:
            return None

        await user.set_password(password)
        await user.save()
        return user

    @staticmethod
    async def verify_user_password(user_id: UUID, password: str) -> bool:
        user = await User.get_or_none(id=user_id)
        if not user:
            return False

        return await user.verify_password(password)

    @staticmethod
    async def record_login_success(
        user_id: UUID, ip_address: str, user_agent: str
    ) -> Optional[User]:
        user = await User.get_or_none(id=user_id)
        if not user:
            return None

        await user.record_login_success(ip_address, user_agent)
        return user

    @staticmethod
    async def record_login_failure(
        user_id: UUID, ip_address: str, user_agent: str
    ) -> Optional[User]:
        user = await User.get_or_none(id=user_id)
        if not user:
            return None

        await user.record_login_failure(ip_address, user_agent)
        return user

    @staticmethod
    async def lock_user_account(user_id: UUID) -> Optional[User]:
        user = await User.get_or_none(id=user_id)
        if not user:
            return None

        user.is_locked = True
        await user.save()
        return user

    @staticmethod
    async def unlock_user_account(user_id: UUID) -> Optional[User]:
        user = await User.get_or_none(id=user_id)
        if not user:
            return None

        user.is_locked = False
        user.failed_login_attempts = 0
        await user.save()
        return user

    @staticmethod
    async def list_users(skip: int = 0, limit: int = 20) -> Tuple[List[User], int]:
        # Get total count for pagination
        count = await User.all().count()

        # Apply pagination
        users = await User.all().offset(skip).limit(limit)

        return users, count
