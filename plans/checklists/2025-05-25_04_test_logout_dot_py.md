# Testing `logout` Endpoint

This checklist outlines the tasks needed to thoroughly test the `logout` endpoint in `backend/src/backend/routes/users/profile/logout.py`. The current test coverage for this file is 65%, and our goal is to achieve 100% coverage.

## Test Setup

- [ ] Create a test file at `backend/tests/routes/users/profile/test_logout.py`
- [ ] Set up necessary test fixtures:
  - [ ] Fixture for an authenticated `User` object (`mock_user`).
  - [ ] Fixture for a mock `Request` object (`mock_request`).
  - [ ] Fixture for mock `UserSession` objects (`mock_session_active`, `mock_session_inactive`, `mock_session_different_ip_agent`).

## Testing `logout` Function

### Successful Logout Scenarios
- [ ] Test logout when user has one active session matching IP and User-Agent:
  - [ ] Verify `HTTP_204_NO_CONTENT` status code is returned.
  - [ ] Verify `current_user.sessions.filter` is called with correct `ip_address`, `user_agent`, and `is_active=True`.
  - [ ] Verify `session.invalidate()` is called on the matching active session.
  - [ ] Verify `UserEvent.log_logout` is called with `current_user.id`, IP address, and User-Agent.
- [ ] Test logout when user has multiple active sessions matching IP and User-Agent:
  - [ ] Verify `session.invalidate()` is called on all matching active sessions.
- [ ] Test logout when user has active sessions, but none match the current IP and User-Agent:
  - [ ] Verify `session.invalidate()` is NOT called.
  - [ ] Verify `UserEvent.log_logout` is still called.
- [ ] Test logout when user has no active sessions at all:
  - [ ] Verify `session.invalidate()` is NOT called.
  - [ ] Verify `UserEvent.log_logout` is still called.
- [ ] Test logout when `request.client` is `None`:
  - [ ] Verify `current_user.sessions.filter` is called with `ip_address=UNKNOWN_IP_ADDRESS_MARKER`.
  - [ ] Verify `UserEvent.log_logout` is called with `UNKNOWN_IP_ADDRESS_MARKER` for IP address.
- [ ] Test logout when `User-Agent` header is missing:
  - [ ] Verify `current_user.sessions.filter` is called with `user_agent=""`.
  - [ ] Verify `UserEvent.log_logout` is called with an empty string for `user_agent`.

### Behavior with Inactive Sessions
- [ ] Test logout when user only has inactive sessions matching IP and User-Agent:
  - [ ] Verify `session.invalidate()` is NOT called (as filter includes `is_active=True`).

## Mock Strategy

- [ ] Create mocks for the following:
  - [ ] `backend.routes.users.profile.logout.get_current_user` (to return the `mock_user`).
  - [ ] `mock_user.sessions.filter().all()`: This will need to be an `AsyncMock` that returns a list of mock session objects based on the test scenario.
  - [ ] `mock_session.invalidate()`: This will be an `AsyncMock` on the mock session objects.
  - [ ] `backend.db.models.user_event.UserEvent.log_logout` class method (as an `AsyncMock`).

## Test Coverage Goals

- [ ] Achieve 100% line coverage for `logout` in `logout.py`.
- [ ] Ensure all conditional branches (e.g., `if request.client else ...`) are tested.
- [ ] Ensure the loop for sessions is tested (empty list, single item, multiple items).

## Documentation

- [ ] Document the testing approach for the `logout` endpoint within the test file or related documentation if necessary, especially the mocking of the session filtering and invalidation.

## Key Lessons Learned

*(This section will be filled in as tests are developed and insights are gained)*

- Example: How to effectively mock chained queryset calls like `user.sessions.filter(...).all()`.
- Example: Verifying calls on items within a list returned by a mock.
