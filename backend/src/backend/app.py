from fastapi import FastAPI

from backend.routes import router
from backend.utils.version import get_version

app = FastAPI(
    title="The Robot Overlord API",
    description="Backend API for The Robot Overlord",
    version=get_version(),
)

app.include_router(router)
