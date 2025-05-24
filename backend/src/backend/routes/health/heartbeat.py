import asyncio

from fastapi import APIRouter
from fastapi import WebSocket

from backend.routes.health.utils import build_health_check_response

router = APIRouter()


@router.websocket("/heartbeat")
async def heartbeat(
    websocket: WebSocket,
) -> None:
    """WebSocket endpoint that sends a heartbeat message every second."""
    await websocket.accept()
    while True:
        message = build_health_check_response()
        await websocket.send_json(message.model_dump())
        await asyncio.sleep(1)
