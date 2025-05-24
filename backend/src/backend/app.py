from importlib.metadata import version
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import asyncio
from datetime import datetime, timezone

# Create FastAPI application
app = FastAPI(
    title="The Robot Overlord API",
    description="Backend API for the Robot Overlord project",
    version=version("backend"),
)


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """Simple health check endpoint to verify the API is running."""
    return JSONResponse(
        content={
            "status": "ok",
            "version": app.version,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
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
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                }
            )
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        # Handle client disconnect gracefully
        pass
