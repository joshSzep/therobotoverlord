# Testing `change_password` Endpoint

This checklist outlines the tasks needed to thoroughly test the `change_password` endpoint in `backend/src/backend/routes/users/profile/change_password.py`. The current test coverage for this file is 58%, and our goal is to achieve 100% coverage.

## Test Setup

- [ ] Create a test file at `backend/tests/routes/users/profile/test_change_password.py`
- [ ] Set up necessary test fixtures:
  - [ ] Fixture for an authenticated `User` object.
  - [ ] Fixture for a mock `Request` object.
  - [ ] Fixture for `PasswordChangeRequestSchema`.

## Testing `change_password` Function

### Successful Password Change
- [ ] Test with a valid current password and a valid new password.
  - [ ] Verify `HTTP_204_NO_CONTENT` status code is returned.
  - [ ] Verify `current_user.set_password` is called with `password_data.new_password`.
  - [ ] Verify `current_user.save` is called.
  - [ ] Verify `UserEvent.log_password_change` is called with `current_user.id`, IP address, and User-Agent.

### Incorrect Current Password
- [ ] Test with an incorrect `current_password`.
  - [ ] Verify `HTTPException` with `status_code=status.HTTP_401_UNAUTHORIZED` is raised.
  - [ ] Verify the detail message is "CITIZEN, YOUR CURRENT PASSWORD IS INCORRECT".

### Invalid New Password
- [ ] Test with a `new_password` that fails validation (e.g., too short, too common).
  - [ ] Verify `HTTPException` with `status_code=status.HTTP_400_BAD_REQUEST` is raised.
  - [ ] Verify the detail message starts with "CITIZEN, YOUR NEW PASSWORD REQUIRES CALIBRATION: ".

### Edge Cases for Request Information
- [ ] Test password change when `request.client` is `None`.
  - [ ] Verify `UserEvent.log_password_change` is called with `UNKNOWN_IP_ADDRESS_MARKER` for IP address.
- [ ] Test password change when `User-Agent` header is missing.
  - [ ] Verify `UserEvent.log_password_change` is called with an empty string for `user_agent`.

## Mock Strategy

- [ ] Create mocks for the following:
  - [ ] `backend.routes.users.profile.change_password.get_current_user` (to return the mock authenticated user).
  - [ ] `User.verify_password` method (for the `current_user` mock).
  - [ ] `backend.routes.users.profile.change_password.validate_password` function.
  - [ ] `User.set_password` method (for the `current_user` mock).
  - [ ] `User.save` method (for the `current_user` mock).
  - [ ] `backend.db.models.user_event.UserEvent.log_password_change` class method.

## Test Coverage Goals

- [ ] Achieve 100% line coverage for `change_password` in `change_password.py`.
- [ ] Ensure all conditional branches (if/else paths) are tested.
- [ ] Ensure all exception handling paths (`HTTPException` raises) are tested.

## Documentation

- [ ] Document the testing approach for the `change_password` endpoint within the test file or related documentation if necessary.

## Key Lessons Learned

*(This section will be filled in as tests are developed and insights are gained)*

- Example: Mocking dependent services effectively.
- Example: Handling specific FastAPI request components in tests.
