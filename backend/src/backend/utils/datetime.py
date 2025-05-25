from datetime import UTC
from datetime import datetime


def now_utc() -> datetime:
    """
    ONLY use this and NEVER use datetime.now() or datetime.utcnow() directly,
    as they are not timezone aware.
    """
    return datetime.now(tz=UTC)
