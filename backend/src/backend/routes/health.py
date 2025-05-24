import asyncio
from datetime import UTC
from datetime import datetime

from fastapi import APIRouter
from fastapi import Request
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from pydantic import BaseModel

# Create a router for health check endpoints
router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


class HealthCheckResponse(BaseModel):
    """Model for health check response data."""

    status: str
    version: str
    timestamp: str


def build_health_check_response(
    version: str,
) -> HealthCheckResponse:
    """Build a health check response."""
    return HealthCheckResponse(
        status="ok",
        version=version,
        timestamp=datetime.now(tz=UTC).isoformat(),
    )


@router.get("/check", response_model=HealthCheckResponse)
async def health_check(
    request: Request,
) -> HealthCheckResponse:
    """Simple health check endpoint to verify the API is running."""
    return build_health_check_response(request.app.version)


@router.websocket("/heartbeat")
async def heartbeat(
    websocket: WebSocket,
) -> None:
    """WebSocket endpoint that sends a heartbeat message every second."""
    await websocket.accept()
    try:
        while True:
            message = build_health_check_response(websocket.app.version)
            await websocket.send_json(message.model_dump())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
