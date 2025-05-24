import re


def test_heartbeat_websocket_message(client):
    """Test that the heartbeat websocket endpoint sends messages."""
    with client.websocket_connect("/health/heartbeat") as websocket:
        # Receive a message
        data = websocket.receive_json()

        # Verify the message structure
        assert "version" in data
        assert "timestamp" in data

        # Verify the message content types
        assert isinstance(data["version"], str)

        # Verify timestamp format (ISO 8601)
        timestamp_pattern = (
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(([+-]\d{2}:\d{2})|Z)"
        )
        assert re.match(timestamp_pattern, data["timestamp"]) is not None
