import re

from backend.routes.health.health_utils import build_health_check_response
from backend.schemas.health import HealthCheckResponseSchema


def test_build_health_check_response():
    """Test the build_health_check_response function."""
    # Call the function
    response = build_health_check_response()

    # Verify the response
    assert isinstance(response, HealthCheckResponseSchema)
    assert isinstance(response.version, str)

    # Verify timestamp format (ISO 8601)
    timestamp_pattern = (
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(([+-]\d{2}:\d{2})|Z)"
    )
    assert re.match(timestamp_pattern, response.timestamp) is not None
