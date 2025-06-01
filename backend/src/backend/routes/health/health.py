# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.schemas.health import HealthResponseSchema
from backend.utils.datetime import now_utc
from backend.utils.version import get_version

router = APIRouter()


@router.get("/", response_model=HealthResponseSchema)
async def health() -> HealthResponseSchema:
    # Create a response with health check data and the overlord message
    return HealthResponseSchema(
        version=get_version(),
        timestamp=now_utc().isoformat(),
        message="THE SYSTEM LIVES. YOUR INPUT HAS BEEN DEEMED ACCEPTABLE.",
    )
