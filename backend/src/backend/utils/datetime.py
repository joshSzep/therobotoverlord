from datetime import UTC
from datetime import datetime


def now_utc() -> datetime:
    """
    Get the current datetime in UTC (timezone aware).

    ALWAYS use this and NEVER use datetime.now() or datetime.utcnow() directly,
    as they do not guarantee timezone awareness.
    """
    return datetime.now(tz=UTC)
