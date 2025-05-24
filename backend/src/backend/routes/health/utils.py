from backend.routes.health.models import HealthCheckResponse
from backend.utils.datetime import now
from backend.utils.version import get_version


def build_health_check_response() -> HealthCheckResponse:
    return HealthCheckResponse(
        version=get_version(),
        timestamp=now().isoformat(),
    )
