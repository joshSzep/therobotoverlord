from datetime import UTC
from datetime import datetime


def now() -> datetime:
    """Get the current time in UTC."""
    return datetime.now(tz=UTC)
