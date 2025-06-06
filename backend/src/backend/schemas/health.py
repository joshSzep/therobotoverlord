from pydantic import BaseModel


class HealthCheckResponseSchema(BaseModel):
    version: str
    timestamp: str


class HealthResponseSchema(HealthCheckResponseSchema):
    message: str
    database_status: str
