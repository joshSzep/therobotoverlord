# Testing `UserEvent` Model and Methods

This checklist outlines the tasks needed to achieve 100% test coverage for the `UserEvent` model and its logging methods in `backend/src/backend/db/models/user_event.py`. The current test coverage for this file is 81%.

## Test Setup

- [ ] Create a test file at `backend/tests/db/models/test_user_event.py`.
- [ ] Set up necessary test fixtures:
  - [ ] Fixture for a sample `user_id` (e.g., `uuid.uuid4()`).
  - [ ] Fixture for sample `ip_address` (e.g., "127.0.0.1").
  - [ ] Fixture for sample `user_agent` (e.g., "TestClient/0.1").

## Testing `UserEvent` Class Methods

For each `log_*` method, ensure the following:
- The method is an `async` class method.
- It calls `UserEvent.create` with the expected arguments.
- The returned `UserEvent` instance (or the arguments passed to `create`) has the correct `event_type`, `user_id`, `ip_address`, and `user_agent`.

- [ ] **Test `log_login_success`**
  - [ ] Verify `UserEvent.create` is called with `event_type="login_success"` and correct user/client info.

- [ ] **Test `log_login_failure`**
  - [ ] Test with a valid `user_id`:
    - [ ] Verify `UserEvent.create` is called with `event_type="login_failure"` and correct user/client info.
  - [ ] Test with `user_id=None`:
    - [ ] Verify `UserEvent.create` is called with `event_type="login_failure"`, `user_id=None`, and correct client info.

- [ ] **Test `log_logout`**
  - [ ] Verify `UserEvent.create` is called with `event_type="logout"` and correct user/client info.

- [ ] **Test `log_password_change`**
  - [ ] Verify `UserEvent.create` is called with `event_type="password_change"` and correct user/client info.

- [ ] **Test `log_account_lockout`**
  - [ ] Verify `UserEvent.create` is called with `event_type="account_lockout"` and correct user/client info.

## Testing Model Fields (Basic Instantiation)

- [ ] Test basic instantiation of `UserEvent` with all fields, including optional ones like `resource_type`, `resource_id`, and `metadata` to ensure model definition is sound (though the `log_*` methods don't use these directly).
  - [ ] This might involve a separate test that directly calls `UserEvent.create` or `UserEvent()` if not covered by testing the `log_*` methods' return values comprehensively.

## Mock Strategy

- [ ] Mock `backend.db.models.user_event.UserEvent.create`:
  - [ ] Use `unittest.mock.patch.object` or `mocker.patch.object` to mock `UserEvent.create` as an `AsyncMock`.
  - [ ] This allows asserting that `create` was called with the correct arguments by each `log_*` method.
  - [ ] Optionally, configure the mock to return a `MagicMock` instance of `UserEvent` if further assertions on the returned object are needed beyond what `create` was called with.

## Test Coverage Goals

- [ ] Achieve 100% line coverage for `user_event.py`.
- [ ] Ensure all parameters and branches within the `log_*` methods are tested (especially the `user_id: uuid.UUID | None` in `log_login_failure`).

## Documentation

- [ ] Briefly document the testing approach, particularly the mocking of `UserEvent.create`.

## Key Lessons Learned

*(This section will be filled in if any non-obvious insights are gained during test implementation)*
