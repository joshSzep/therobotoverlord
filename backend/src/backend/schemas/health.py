from pydantic import BaseModel


class HealthCheckResponseSchema(BaseModel):
    version: str
    timestamp: str
