from datetime import UTC
from datetime import datetime

from backend.utils.datetime import now


def test_now():
    """Test the now function returns a datetime in UTC."""
    # Get the current time using the utility function
    current_time = now()

    # Verify it's a datetime object
    assert isinstance(current_time, datetime)

    # Verify it's in UTC timezone
    assert current_time.tzinfo == UTC
