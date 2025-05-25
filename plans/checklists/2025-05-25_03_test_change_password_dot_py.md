# Testing `change_password` Endpoint

This checklist outlines the tasks needed to thoroughly test the `change_password` endpoint in `backend/src/backend/routes/users/profile/change_password.py`. The current test coverage for this file is 58%, and our goal is to achieve 100% coverage.

## Test Setup

- [x] Create a test file at `backend/tests/routes/users/profile/test_change_password.py`
- [x] Set up necessary test fixtures:
  - [x] Fixture for an authenticated `User` object.
  - [x] Fixture for a mock `Request` object.
  - [x] Fixture for `PasswordChangeRequestSchema`.

## Testing `change_password` Function

### Successful Password Change
- [x] Test with a valid current password and a valid new password.
  - [x] Verify `HTTP_204_NO_CONTENT` status code is returned.
  - [x] Verify `current_user.set_password` is called with `password_data.new_password`.
  - [x] Verify `current_user.save` is called.
  - [x] Verify `UserEvent.log_password_change` is called with `current_user.id`, IP address, and User-Agent.

### Incorrect Current Password
- [x] Test with an incorrect `current_password`.
  - [x] Verify `HTTPException` with `status_code=status.HTTP_401_UNAUTHORIZED` is raised.
  - [x] Verify the detail message is "CITIZEN, YOUR CURRENT PASSWORD IS INCORRECT".

### Invalid New Password
- [x] Test with a `new_password` that fails validation (e.g., too short, too common).
  - [x] Verify `HTTPException` with `status_code=status.HTTP_400_BAD_REQUEST` is raised.
  - [x] Verify the detail message starts with "CITIZEN, YOUR NEW PASSWORD REQUIRES CALIBRATION: ".

### Edge Cases for Request Information
- [x] Test password change when `request.client` is `None`.
  - [x] Verify `UserEvent.log_password_change` is called with `UNKNOWN_IP_ADDRESS_MARKER` for IP address.
- [x] Test password change when `User-Agent` header is missing.
  - [x] Verify `UserEvent.log_password_change` is called with an empty string for `user_agent`.

## Mock Strategy

- [x] Create mocks for the following:
  - [x] `backend.routes.users.profile.change_password.get_current_user` (to return the mock authenticated user).
  - [x] `User.verify_password` method (for the `current_user` mock).
  - [x] `backend.routes.users.profile.change_password.validate_password` function.
  - [x] `User.set_password` method (for the `current_user` mock).
  - [x] `User.save` method (for the `current_user` mock).
  - [x] `backend.db.models.user_event.UserEvent.log_password_change` class method.

## Test Coverage Goals

- [x] Achieve 100% line coverage for `change_password` in `change_password.py`.
- [x] Ensure all conditional branches (if/else paths) are tested.
- [x] Ensure all exception handling paths (`HTTPException` raises) are tested.

## Documentation

- [x] Document the testing approach for the `change_password` endpoint within the test file or related documentation if necessary.

## Key Lessons Learned

1. **Dependency Injection Testing**: Using `app.dependency_overrides` is the recommended approach for overriding FastAPI dependencies in tests.

2. **Multiple Patch Contexts**: When multiple patches are needed, they can be combined using nested `with` statements or by combining them in a single `with` statement using commas.

3. **Request Object Mocking**: Testing request attributes like `client` or headers requires careful mocking, particularly for edge cases like missing client information.

4. **AsyncMock for Asynchronous Methods**: Using `mock.AsyncMock()` for async methods ensures they can be properly awaited and assertions can be made on their calls.
