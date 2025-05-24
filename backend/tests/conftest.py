from fastapi.testclient import TestClient
import pytest

from backend.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)
