# Standard library imports
import asyncio

# Third-party imports
from fastapi import APIRouter
from fastapi import WebSocket

# Project-specific imports
from backend.schemas.health import HealthCheckResponseSchema
from backend.utils.datetime import now_utc
from backend.utils.version import get_version

router = APIRouter()


HEARTBEAT_INTERVAL_SECONDS: float = 1.0


@router.websocket("/heartbeat/")
async def heartbeat(
    websocket: WebSocket,
) -> None:
    await websocket.accept()
    while True:
        message: HealthCheckResponseSchema = HealthCheckResponseSchema(
            version=get_version(),
            timestamp=now_utc().isoformat(),
        )
        await websocket.send_json(message.model_dump())
        await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)
