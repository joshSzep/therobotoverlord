# Standard library imports
from datetime import datetime

# Third-party imports
from jinja2 import Environment as Jinja2Environment


def datetime_filter(value: datetime | None) -> str:
    """Format a datetime object to a human-readable string."""
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M")


def truncate(value: str, length: int = 100) -> str:
    """Truncate a string to a specified length."""
    if not value:
        return ""
    if len(value) <= length:
        return value
    return value[:length] + "..."


def nl2br(value: str) -> str:
    """Convert newlines to <br> tags."""
    if not value:
        return ""
    return value.replace("\n", "<br>")


def setup_jinja_filters(env: Jinja2Environment) -> None:
    """Set up Jinja2 filters."""
    env.filters["datetime"] = datetime_filter
    env.filters["truncate"] = truncate
    env.filters["nl2br"] = nl2br
