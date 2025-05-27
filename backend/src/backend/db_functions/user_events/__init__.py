"""
User event-related data access functions.

This module provides functions for working with user events in the database.
"""

from backend.db_functions.user_events.count_recent_failed_login_attempts import (
    count_recent_failed_login_attempts,
)
from backend.db_functions.user_events.create_event import create_event
from backend.db_functions.user_events.create_login_attempt import create_login_attempt
from backend.db_functions.user_events.get_recent_failed_login_attempts import (
    get_recent_failed_login_attempts,
)
from backend.db_functions.user_events.get_recent_login_attempts import (
    get_recent_login_attempts,
)
from backend.db_functions.user_events.get_user_events import get_user_events
from backend.db_functions.user_events.list_login_attempts import list_login_attempts
from backend.db_functions.user_events.log_account_lockout import log_account_lockout
from backend.db_functions.user_events.log_login_failure import log_login_failure
from backend.db_functions.user_events.log_login_success import log_login_success
from backend.db_functions.user_events.log_logout import log_logout
from backend.db_functions.user_events.log_password_change import log_password_change

__all__ = [
    "count_recent_failed_login_attempts",
    "create_event",
    "create_login_attempt",
    "get_recent_failed_login_attempts",
    "get_recent_login_attempts",
    "get_user_events",
    "list_login_attempts",
    "log_account_lockout",
    "log_login_failure",
    "log_login_success",
    "log_logout",
    "log_password_change",
]
