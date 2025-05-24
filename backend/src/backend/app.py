from importlib.metadata import version

from fastapi import FastAPI

from backend.routes.health import router as health_router

app = FastAPI(
    title="The Robot Overlord API",
    description="Backend API for The Robot Overlord",
    version=version("backend"),
)

app.include_router(health_router)
