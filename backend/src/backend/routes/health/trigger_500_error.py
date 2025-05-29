# Standard library imports
import logging

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException

router = APIRouter()


@router.get("/trigger-500-error/")
async def trigger_500_error() -> None:
    """
    Deliberately trigger a 500 Internal Server Error.

    This endpoint is used for testing error handling and server error detection.
    It logs an ERROR level message and raises an exception.
    """
    # Log an error message
    logging.error("DELIBERATE ERROR: This error was triggered for testing purposes")

    # Raise an exception that will cause a 500 Internal Server Error
    raise HTTPException(
        status_code=500, detail="Internal Server Error triggered for testing"
    )
