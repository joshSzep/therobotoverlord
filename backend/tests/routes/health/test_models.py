from pydantic import ValidationError
import pytest

from backend.routes.health.models import HealthCheckResponse


def test_health_check_response_valid_data():
    """Test creating a HealthCheckResponse with valid data."""
    # Create a valid response
    response = HealthCheckResponse(
        version="1.0.0", timestamp="2025-05-24T09:15:00+00:00"
    )

    # Verify the fields are set correctly
    assert response.version == "1.0.0"
    assert response.timestamp == "2025-05-24T09:15:00+00:00"


def test_health_check_response_missing_fields():
    """Test that HealthCheckResponse requires all fields."""
    # Test missing version
    with pytest.raises(ValidationError):
        HealthCheckResponse(timestamp="2025-05-24T09:15:00+00:00")

    # Test missing timestamp
    with pytest.raises(ValidationError):
        HealthCheckResponse(version="1.0.0")


def test_health_check_response_model_dump():
    """Test that HealthCheckResponse can be serialized to a dict."""
    response = HealthCheckResponse(
        version="1.0.0", timestamp="2025-05-24T09:15:00+00:00"
    )

    # Test model_dump method
    data = response.model_dump()
    assert isinstance(data, dict)
    assert data["version"] == "1.0.0"
    assert data["timestamp"] == "2025-05-24T09:15:00+00:00"
