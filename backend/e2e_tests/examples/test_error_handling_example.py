"""
Example test demonstrating how to use the ignore_server_errors marker.

This file is for demonstration purposes only and is not meant to be run as part of the
regular test suite. It shows how to properly test error conditions without triggering
the automatic server error detection.
"""

import httpx
import pytest


@pytest.mark.ignore_server_errors
async def test_error_handling_example(api_client: httpx.AsyncClient):
    """
    Example test that demonstrates how to use the ignore_server_errors marker.

    This test intentionally triggers a server error by requesting a non-existent
    endpoint. Without the ignore_server_errors marker, this test would fail due to
    the server error detection mechanism, even though we're testing error handling.
    """
    # This would normally cause the test to fail due to server error detection
    response = await api_client.get("/non-existent-endpoint/")

    # We can still assert on the response status code
    assert response.status_code == 404, "Expected a 404 Not Found response"

    # We can also check the response body
    assert "Not Found" in response.text, "Response should contain 'Not Found'"

    # The test will pass even if the server logs contain ERROR messages
    # because we've marked it with @pytest.mark.ignore_server_errors
