import asyncio
from datetime import UTC
from datetime import datetime
from importlib.metadata import version

from fastapi import FastAPI
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from fastapi.responses import JSONResponse

# Create FastAPI application
app = FastAPI(
    title="The Robot Overlord API",
    description="Backend API for The Robot Overlord",
    version=version("backend"),
)


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """Simple health check endpoint to verify the API is running."""
    return JSONResponse(
        content={
            "status": "ok",
            "version": app.version,
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }
    )


@app.websocket("/ws/heartbeat")
async def heartbeat(websocket: WebSocket) -> None:
    """WebSocket endpoint that sends a heartbeat message every second."""
    await websocket.accept()
    try:
        while True:
            # Send heartbeat message every second
            await websocket.send_json(
                {
                    "type": "heartbeat",
                    "version": app.version,
                    "timestamp": datetime.now(tz=UTC).isoformat(),
                }
            )
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        # Handle client disconnect gracefully
        pass
