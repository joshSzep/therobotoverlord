"""TEMPORARY Tests for the profile endpoints package structure."""

import pytest

from backend.routes.users.profile import router
from backend.utils.constants import UNKNOWN_IP_ADDRESS_MARKER


@pytest.mark.asyncio
async def test_profile_router_endpoints():
    """Test that the profile router has the expected endpoints."""
    # Simply check that the router has exactly 3 routes
    assert len(router.routes) == 3

    # Check for the specific endpoint strings we expect
    route_strings = [str(route) for route in router.routes]

    # Check for the specific endpoints we expect
    assert any("/profile/me" in path for path in route_strings)
    assert any("/profile/change-password" in path for path in route_strings)
    assert any("/profile/logout" in path for path in route_strings)


def test_constants_imported():
    """Test that constants are properly imported from the utils module."""
    assert UNKNOWN_IP_ADDRESS_MARKER == "<UNKNOWN_IP_ADDRESS>"
