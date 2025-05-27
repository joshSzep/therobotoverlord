# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.health.health_utils import build_health_check_response
from backend.schemas.health import HealthCheckResponseSchema

router = APIRouter()


@router.get("/check/", response_model=HealthCheckResponseSchema)
async def check() -> HealthCheckResponseSchema:
    return build_health_check_response()
