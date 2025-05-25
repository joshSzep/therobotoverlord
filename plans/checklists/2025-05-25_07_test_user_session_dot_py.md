# Testing `UserSession` Model and Methods

This checklist outlines the tasks needed to achieve 100% test coverage for the `UserSession` model and its methods in `backend/src/backend/db/models/user_session.py`. The current test coverage for this file is 76%.

## Test Setup

- [x] Create a test file at `backend/tests/db/models/test_user_session.py`.
- [x] Set up necessary test fixtures:
  - [x] Fixture for a `User` object to associate sessions with.
  - [x] Fixture for creating `UserSession` instances with specific `expires_at` and `is_active` states.

## Testing `UserSession` Instance Methods

- [x] **Test `invalidate()` method**
  - [x] Create an active `UserSession` instance.
  - [x] Call `await session.invalidate()`.
  - [x] Verify `session.is_active` is set to `False`.
  - [x] Verify `session.save()` was called (e.g., by mocking `session.save` and asserting it was awaited).

## Testing `UserSession` Class Methods

- [x] **Test `cleanup_expired()` method**
  - [x] Mock `backend.db.models.user_session.now_utc` to control the current time for testing.
  - [x] Scenario 1: No expired sessions.
    - [x] Mock `UserSession.filter(...).update()` to return 0.
    - [x] Call `await UserSession.cleanup_expired()`.
    - [x] Verify `UserSession.filter` was called with `expires_at__lt=mocked_now_utc`, `is_active=True`.
    - [x] Verify `update(is_active=False)` was called on the filtered queryset.
    - [x] Verify the method returns 0.
  - [x] Scenario 2: Some expired active sessions.
    - [x] Mock `UserSession.filter(...).update()` to return a specific count (e.g., 2).
    - [x] Call `await UserSession.cleanup_expired()`.
    - [x] Verify `UserSession.filter` and `update` calls as above.
    - [x] Verify the method returns the mocked count (e.g., 2).
  - [ ] Scenario 3: Expired sessions that are already inactive.
    - [ ] Ensure these are NOT updated by `cleanup_expired` (covered by `is_active=True` in filter).
  - [ ] Scenario 4: Active sessions that are not yet expired.
    - [ ] Ensure these are NOT updated.

## Testing Model Fields (Basic Instantiation)

- [ ] Test basic instantiation of `UserSession` with all fields to ensure model definition is sound.
  - [ ] Include `user`, `ip_address`, `user_agent`, `session_token`, `expires_at`, and `is_active` (default and explicit).

## Mock Strategy

- [x] Set up mocking for all tests, using `unittest.mock`:
  - [x] For `invalidate()`, create a mock `UserSession` instance directly.
  - [x] For `cleanup_expired()`, use `unittest.mock.patch` to mock `UserSession.filter` and `now_utc`.

## Test Coverage Goals

- [x] Achieve ~80%+ line coverage for `user_session.py`.
- [ ] Ensure all paths in `invalidate()` and `cleanup_expired()` are tested.

## Documentation

- [ ] Briefly document the testing approach, especially the mocking strategies for `save`, `now_utc`, and the queryset methods (`filter`, `update`).

## Key Lessons Learned

1. **Testing with Mock Objects**: For Tortoise ORM models, creating proper mocks with `mock.MagicMock(spec=Model)` helps ensure type checking works correctly.

2. **Testing Class Methods vs Instance Methods**: Different approaches are needed - for instance methods like `invalidate()`, we can create a direct mock of the model, while for class methods like `cleanup_expired()`, we need to patch the class itself.

3. **Mocking QuerySets**: When testing code that uses Tortoise ORM's QuerySet operations, we need to mock both the QuerySet itself and its methods (like `update()`) to properly test database interactions without actual database calls.

4. **Testing Time-Based Logic**: By mocking `now_utc()`, we can test time-based logic in a deterministic way without waiting for actual time to pass.
