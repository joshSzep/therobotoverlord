from fastapi import APIRouter

from backend.routes.health.health_schemas import HealthCheckResponseSchema
from backend.routes.health.health_utils import build_health_check_response

router = APIRouter()


@router.get("/check", response_model=HealthCheckResponseSchema)
async def check() -> HealthCheckResponseSchema:
    """Simple health check endpoint to verify the API is running."""
    return build_health_check_response()
