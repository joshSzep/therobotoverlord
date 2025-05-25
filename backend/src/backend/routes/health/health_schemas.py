from pydantic import BaseModel


class HealthCheckResponseSchema(BaseModel):
    """Schema for health check response data."""

    version: str
    timestamp: str
