def test_health_endpoint(client):
    """Test the health endpoint returns 200 and correct structure."""
    # Make a request to the health endpoint
    response = client.get("/health/")

    # Verify the response status code
    assert response.status_code == 200

    # Verify the response structure
    data = response.json()
    assert "version" in data
    assert "timestamp" in data
    assert "message" in data

    # Verify the response data types
    assert isinstance(data["version"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["message"], str)

    # Verify the message content
    assert data["message"] == "THE SYSTEM LIVES. YOUR INPUT HAS BEEN DEEMED ACCEPTABLE."
