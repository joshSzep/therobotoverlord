from fastapi import APIRouter

from backend.routes.health.models import HealthCheckResponse
from backend.routes.health.utils import build_health_check_response

router = APIRouter()


@router.get("/check", response_model=HealthCheckResponse)
async def check() -> HealthCheckResponse:
    """Simple health check endpoint to verify the API is running."""
    return build_health_check_response()
