# E2E Testing Framework

This directory contains end-to-end (E2E) tests for The Robot Overlord project. These tests verify that the entire application works correctly from the user's perspective.

## Server Error Detection

The E2E testing framework includes an automatic server error detection mechanism that will fail tests if server errors are detected. This helps catch unexpected errors that might otherwise go unnoticed.

### How It Works

1. The `server_logs` fixture captures all server logs during test execution
2. A pytest hook (`pytest_runtest_makereport`) automatically checks for:
   - ERROR level logs in the server logs
   - 500 status codes in responses
3. If errors are detected, the test is automatically failed with detailed information

### Customizing Error Detection

#### Whitelisting Error Patterns

Some errors might be expected or irrelevant to your test. You can whitelist these errors by adding patterns to the `WHITELISTED_ERROR_PATTERNS` list in `conftest.py`:

```python
WHITELISTED_ERROR_PATTERNS: List[Pattern] = [
    re.compile(r"Expected error pattern"),
    # Add more patterns as needed
]
```

See [whitelist_example.py](examples/whitelist_example.py) for more examples of how to use whitelist patterns.

#### Ignoring Server Errors for Specific Tests

If you have a test that intentionally triggers server errors (e.g., testing error handling), you can mark it to ignore server errors:

```python
@pytest.mark.ignore_server_errors
async def test_that_triggers_errors():
    # This test will not fail due to server errors
    ...
```

See [test_error_handling_example.py](examples/test_error_handling_example.py) for a complete example of how to use the ignore_server_errors marker.

### Benefits

- **Automatic Detection**: No need to manually check for server errors in each test
- **Improved Reliability**: Tests fail if the server encounters unexpected errors
- **Detailed Error Information**: Error messages include server logs and response details
- **Customizable**: Whitelist expected errors and ignore errors for specific tests

### Example

Without this system, a test might pass even if the server logs errors:

```python
async def test_example():
    # Test passes even if server logs errors
    response = await api_client.get("/some/endpoint/")
    assert response.status_code == 200
```

With this system, the test will automatically fail if server errors are detected, even if the assertions pass.
