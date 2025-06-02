# Third-party imports
from fastapi import APIRouter
from tortoise import Tortoise
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.schemas.health import HealthResponseSchema
from backend.utils.datetime import now_utc
from backend.utils.version import get_version

router = APIRouter()


async def check_database_connection() -> str:
    """Check if the database connection is working."""
    try:
        # Try to execute a simple query to check the connection
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
        return "OPERATIONAL"
    except OperationalError:
        return "NOT OPERATIONAL"
    except Exception:
        return "ERROR"


@router.get("/", response_model=HealthResponseSchema)
async def health() -> HealthResponseSchema:
    # Check database connection
    db_status = await check_database_connection()

    # Create a response with health check data and the overlord message
    return HealthResponseSchema(
        version=get_version(),
        timestamp=now_utc().isoformat(),
        message="THE SYSTEM LIVES. YOUR INPUT HAS BEEN DEEMED ACCEPTABLE.",
        database_status=db_status,
    )
