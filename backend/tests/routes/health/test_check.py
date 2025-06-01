import pytest


@pytest.mark.skip(reason="/health/check endpoint has been removed and consolidated")
def test_check_endpoint(client):
    """Test the health check endpoint returns 200 and correct structure."""
    # This test is skipped because the /health/check endpoint has been removed
    # and consolidated into the /health/ endpoint in our refactoring.
    # See test_health.py for tests of the new endpoint.
    pass
