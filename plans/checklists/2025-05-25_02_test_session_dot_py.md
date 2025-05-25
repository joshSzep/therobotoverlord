# Testing Tasks for Session Management

This checklist outlines the tasks needed to thoroughly test the session management background tasks in `backend/src/backend/tasks/session.py`. The current test coverage is at ~~38%~~ **100%**, and our goal is to achieve 100% coverage.

## Test Setup

- [x] Create a test file at `backend/tests/tasks/test_session.py`
- [x] Set up necessary test fixtures:
  - [x] Create fixture for expired sessions
  - [x] Create fixture for active sessions
  - [x] Create fixture for mocking database initialization/connection

## Testing `cleanup_expired_sessions` Function

- [x] Test basic cleanup functionality:
  - [x] Test cleaning up when there are expired sessions
  - [x] Test returning correct count of cleaned up sessions
  - [x] Verify that only expired sessions are removed (active sessions remain)

- [x] Test database connection handling:
  - [x] Test when database is not initialized (should initialize)
  - [x] Test when database is already initialized (should not reinitialize)
  - [x] Test proper connection closing in the finally block

- [x] Test error handling:
  - [x] Test behavior when an exception occurs during cleanup
  - [x] Verify error is logged properly
  - [x] Verify function returns 0 when an error occurs
  - [x] Verify database connection is closed even when an error occurs

## Testing `run_session_cleanup_task` Function

- [x] Test periodic execution:
  - [x] Test that cleanup function is called at regular intervals
  - [x] Test with different interval settings
  - [x] Test execution with custom interval parameter

- [x] Test cancellation:
  - [x] Test proper handling when the task is cancelled
  - [x] Test for resource cleanup when task is cancelled

## Mock Strategy

- [x] Create mocks for the following:
  - [x] `UserSession.cleanup_expired()` method
  - [x] `Tortoise.init()` method
  - [x] `Tortoise.close_connections()` method
  - [x] `asyncio.sleep()` function
  - [x] Logger for testing log messages

## Integration Testing

- [x] Test integration with UserSession model:
  - [x] ~~Verify that actual expired sessions are properly cleaned up~~ Implemented with mocks instead of actual DB operations
  - [x] ~~Verify that actual active sessions are not affected~~ Implemented with mocks instead of actual DB operations

## Utility Functions

- [x] Create helper functions for testing:
  - [x] ~~Create function to generate test sessions with specific expiration dates~~ Used fixtures instead
  - [x] ~~Create function to verify session state after cleanup~~ Used direct assertions instead

## Test Coverage Goals

- [x] Achieve 100% line coverage for `cleanup_expired_sessions`
- [x] Achieve 100% line coverage for `run_session_cleanup_task`
- [x] Ensure all conditional branches are tested (if/else paths)
- [x] Ensure all exception handling paths are tested

## Documentation

- [x] Document testing approach for background tasks
- [x] Document mocking strategy for periodic tasks
- [x] Update coverage reports to reflect improvements

## Key Lessons Learned

1. **Proper Mocking of Async Code**: Using `mock.AsyncMock()` is essential for testing async functions, particularly when mocking methods that will be awaited.

2. **Handling Private Properties**: When patching private properties like `Tortoise._inited`, it's important to understand the implementation details and use `PropertyMock` with side effects when appropriate.

3. **Breaking Infinite Loops**: For testing functions with infinite loops like `run_session_cleanup_task`, use `mock.AsyncMock(side_effect=[None, Exception("Stop loop")])` to break out after a specific number of iterations.

4. **Testing Cancellation**: For async tasks, testing cancellation scenarios requires creating a real asyncio task and then canceling it, which tests both the cancellation behavior and ensures resources are properly cleaned up.

5. **Avoiding DB Operations in Unit Tests**: Rather than testing with real database operations, we used mocks to isolate the functions being tested and make the tests more reliable and faster.
