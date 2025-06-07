# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.html.posts.create_reply import create_reply_handler

# Create router
router = APIRouter()

# Define routes
router.add_api_route(
    path="/reply/",
    endpoint=create_reply_handler,
    methods=["POST"],
)
