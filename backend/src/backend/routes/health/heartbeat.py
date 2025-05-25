import asyncio

from fastapi import APIRouter
from fastapi import WebSocket

from backend.routes.health.health_schemas import HealthCheckResponseSchema
from backend.routes.health.health_utils import build_health_check_response

router = APIRouter()


HEARTBEAT_INTERVAL_SECONDS: float = 1.0


@router.websocket("/heartbeat")
async def heartbeat(
    websocket: WebSocket,
) -> None:
    await websocket.accept()
    while True:
        message: HealthCheckResponseSchema = build_health_check_response()
        await websocket.send_json(message.model_dump())
        await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)
