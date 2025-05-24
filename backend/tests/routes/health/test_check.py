def test_check_endpoint(client):
    """Test the health check endpoint returns 200 and correct structure."""
    # Make a request to the health check endpoint
    response = client.get("/health/check")

    # Verify the response status code
    assert response.status_code == 200

    # Verify the response structure
    data = response.json()
    assert "version" in data
    assert "timestamp" in data

    # Verify the response data types
    assert isinstance(data["version"], str)
    assert isinstance(data["timestamp"], str)
