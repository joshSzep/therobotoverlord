from backend.schemas.health import HealthCheckResponseSchema
from backend.utils.datetime import now_utc
from backend.utils.version import get_version


def build_health_check_response() -> HealthCheckResponseSchema:
    return HealthCheckResponseSchema(
        version=get_version(),
        timestamp=now_utc().isoformat(),
    )
