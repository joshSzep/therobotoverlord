# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.schemas.health import HealthCheckResponseSchema
from backend.utils.datetime import now_utc
from backend.utils.version import get_version

router = APIRouter()


@router.get("/check/", response_model=HealthCheckResponseSchema)
async def check() -> HealthCheckResponseSchema:
    return HealthCheckResponseSchema(
        version=get_version(),
        timestamp=now_utc().isoformat(),
    )
