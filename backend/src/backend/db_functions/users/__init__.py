"""
User-related data access functions.

This module provides functions for working with users in the database.
"""

from backend.db_functions.users.create_user import create_user
from backend.db_functions.users.get_user_by_email import get_user_by_email
from backend.db_functions.users.get_user_by_id import get_user_by_id
from backend.db_functions.users.list_users import list_users
from backend.db_functions.users.lock_user_account import lock_user_account
from backend.db_functions.users.record_login_failure import record_login_failure
from backend.db_functions.users.record_login_success import record_login_success
from backend.db_functions.users.set_user_password import set_user_password
from backend.db_functions.users.set_user_role import set_user_role
from backend.db_functions.users.unlock_user_account import unlock_user_account
from backend.db_functions.users.update_user import update_user
from backend.db_functions.users.verify_user_password import verify_user_password

__all__ = [
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "list_users",
    "lock_user_account",
    "record_login_failure",
    "record_login_success",
    "set_user_password",
    "set_user_role",
    "unlock_user_account",
    "update_user",
    "verify_user_password",
]
