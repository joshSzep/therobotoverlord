# Testing `UserSession` Model and Methods

This checklist outlines the tasks needed to achieve 100% test coverage for the `UserSession` model and its methods in `backend/src/backend/db/models/user_session.py`. The current test coverage for this file is 76%.

## Test Setup

- [ ] Create a test file at `backend/tests/db/models/test_user_session.py`.
- [ ] Set up necessary test fixtures:
  - [ ] Fixture for a `User` object to associate sessions with.
  - [ ] Fixture for creating `UserSession` instances with specific `expires_at` and `is_active` states.

## Testing `UserSession` Instance Methods

- [ ] **Test `invalidate()` method**
  - [ ] Create an active `UserSession` instance.
  - [ ] Call `await session.invalidate()`.
  - [ ] Verify `session.is_active` is set to `False`.
  - [ ] Verify `session.save()` was called (e.g., by mocking `session.save` and asserting it was awaited).

## Testing `UserSession` Class Methods

- [ ] **Test `cleanup_expired()` method**
  - [ ] Mock `backend.db.models.user_session.now_utc` to control the current time for testing.
  - [ ] Scenario 1: No expired sessions.
    - [ ] Mock `UserSession.filter(...).update()` to return 0.
    - [ ] Call `await UserSession.cleanup_expired()`.
    - [ ] Verify `UserSession.filter` was called with `expires_at__lt=mocked_now_utc`, `is_active=True`.
    - [ ] Verify `update(is_active=False)` was called on the filtered queryset.
    - [ ] Verify the method returns 0.
  - [ ] Scenario 2: Some expired active sessions.
    - [ ] Mock `UserSession.filter(...).update()` to return a specific count (e.g., 2).
    - [ ] Call `await UserSession.cleanup_expired()`.
    - [ ] Verify `UserSession.filter` and `update` calls as above.
    - [ ] Verify the method returns the mocked count (e.g., 2).
  - [ ] Scenario 3: Expired sessions that are already inactive.
    - [ ] Ensure these are NOT updated by `cleanup_expired` (covered by `is_active=True` in filter).
  - [ ] Scenario 4: Active sessions that are not yet expired.
    - [ ] Ensure these are NOT updated.

## Testing Model Fields (Basic Instantiation)

- [ ] Test basic instantiation of `UserSession` with all fields to ensure model definition is sound.
  - [ ] Include `user`, `ip_address`, `user_agent`, `session_token`, `expires_at`, and `is_active` (default and explicit).

## Mock Strategy

- [ ] For `invalidate()`:
  - [ ] Mock the `self.save` method of the `UserSession` instance using `unittest.mock.AsyncMock` to assert it's called.
- [ ] For `cleanup_expired()`:
  - [ ] Mock `backend.db.models.user_session.now_utc` using `unittest.mock.patch` to return a fixed `datetime` object.
  - [ ] Mock `UserSession.filter` to return a mock queryset object.
  - [ ] Mock the `update` method on this mock queryset object (e.g., `mock_queryset.update = unittest.mock.AsyncMock(return_value=expected_count)`).

## Test Coverage Goals

- [ ] Achieve 100% line coverage for `user_session.py`.
- [ ] Ensure all paths in `invalidate()` and `cleanup_expired()` are tested.

## Documentation

- [ ] Briefly document the testing approach, especially the mocking strategies for `save`, `now_utc`, and the queryset methods (`filter`, `update`).

## Key Lessons Learned

*(This section will be filled in if any non-obvious insights are gained during test implementation)*
