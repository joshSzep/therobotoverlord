from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Model for health check response data."""

    version: str
    timestamp: str
