# DB Functions Test Coverage Checklist

## Overview

This checklist provides a structured approach to increase test coverage for all database functions in the Robot Overlord project. The focus is on testing all functions in the `backend/src/backend/db_functions` directory following the project's established patterns and best practices.

## General Testing Guidelines

1. **Follow Project Structure**: Create test files that mirror the structure of the source code
2. **Use Proper Mocking**: Use `mock.patch.object` instead of directly assigning to class attributes
3. **Test All Paths**: Include tests for success cases, error cases, database errors, and edge cases
4. **Follow AAA Pattern**: Structure tests using Arrange-Act-Assert pattern
5. **Use Fixtures**: Create reusable fixtures for common test data
6. **Respect RULE #10**: Explicitly verify that db_functions only directly operate on their own model
7. **Test Transaction Handling**: For functions that perform multiple operations, test what happens if one operation fails
8. **Avoid Datetime Comparisons**: Skip direct datetime comparisons or use appropriate comparison methods

## Test Structure

For each db_function, create a corresponding test file in the `backend/tests/db_functions` directory with the same hierarchical structure. For example:

```
backend/src/backend/db_functions/users/get_user_by_id.py
```

should have a corresponding test file:

```
backend/tests/db_functions/users/test_get_user_by_id.py
```

## Testing Priority

Focus on testing db_functions in the following order of priority:

1. **Core User Functions**: Authentication and user management functions
2. **Event Logging Functions**: Functions that record system events
3. **Session Management**: Functions that handle user sessions
4. **Content Management**: Functions that handle posts, topics, and tags

## Checklist by Module

### Users Module

- [x] **get_user_by_id.py**
  - [x] Test successful retrieval
  - [x] Test when user doesn't exist
  - [x] Test with invalid UUID
  - [x] Test database errors

- [x] **get_user_by_email.py**
  - [x] Test successful retrieval
  - [x] Test when user doesn't exist
  - [x] Test database errors

- [x] **create_user.py**
  - [x] Test successful creation
  - [x] Test with duplicate email
  - [x] Test password hashing
  - [x] Test set_password failure

- [x] **verify_user_password.py** ✅
  - [x] Test with correct password
  - [x] Test with incorrect password
  - [x] Test when user doesn't exist
  - [x] Test database errors
  - [x] Test bcrypt exceptions

- [ ] **update_user.py**
  - [ ] Test successful update
  - [ ] Test when user doesn't exist
  - [ ] Test partial updates
  - [ ] Test database errors

- [ ] **set_user_password.py**
  - [ ] Test successful password change
  - [ ] Test when user doesn't exist
  - [ ] Test password hashing

- [ ] **record_login_success.py**
  - [ ] Test successful login recording
  - [ ] Test when user doesn't exist
  - [ ] Verify user fields are updated correctly
  - [ ] Verify proper delegation to log_login_success

- [ ] **record_login_failure.py**
  - [ ] Test failed login recording
  - [ ] Test when user doesn't exist
  - [ ] Test account lockout after 5 failures
  - [ ] Verify proper delegation to log_login_failure
  - [ ] Verify proper delegation to log_account_lockout

- [ ] **lock_user_account.py**
  - [ ] Test successful account locking
  - [ ] Test when user doesn't exist
  - [ ] Test when account is already locked

- [ ] **unlock_user_account.py**
  - [ ] Test successful account unlocking
  - [ ] Test when user doesn't exist
  - [ ] Test when account is already unlocked

- [ ] **list_users.py**
  - [ ] Test successful listing
  - [ ] Test pagination
  - [ ] Test filtering

### User Events Module

- [ ] **create_event.py**
  - [ ] Test successful event creation
  - [ ] Test with various event types
  - [ ] Test with and without user_id

- [ ] **log_login_success.py**
  - [ ] Test successful event logging
  - [ ] Verify correct metadata

- [ ] **log_login_failure.py**
  - [ ] Test successful event logging
  - [ ] Test with and without user_id
  - [ ] Verify correct metadata

- [ ] **log_account_lockout.py**
  - [ ] Test successful event logging
  - [ ] Verify correct metadata

- [ ] **log_logout.py**
  - [ ] Test successful event logging
  - [ ] Verify correct metadata

- [ ] **log_password_change.py**
  - [ ] Test successful event logging
  - [ ] Verify correct metadata

- [ ] **get_user_events.py**
  - [ ] Test successful retrieval
  - [ ] Test pagination
  - [ ] Test filtering by event type

- [ ] **get_recent_login_attempts.py**
  - [ ] Test successful retrieval
  - [ ] Test with limit parameter
  - [ ] Test with no login attempts

- [ ] **count_recent_failed_login_attempts.py**
  - [ ] Test with failed attempts
  - [ ] Test with no failed attempts
  - [ ] Test with time window parameter

### User Sessions Module

- [ ] **create_session.py**
  - [ ] Test successful session creation
  - [ ] Test with various parameters
  - [ ] Verify expiration time calculation

- [ ] **get_session_by_token.py**
  - [ ] Test successful retrieval
  - [ ] Test with invalid token
  - [ ] Test with expired token

- [ ] **validate_session.py**
  - [ ] Test with valid session
  - [ ] Test with expired session
  - [ ] Test with inactive session

- [ ] **deactivate_session.py**
  - [ ] Test successful deactivation
  - [ ] Test when session doesn't exist
  - [ ] Test when session is already inactive

- [ ] **deactivate_all_user_sessions.py**
  - [ ] Test successful deactivation of all sessions
  - [ ] Test when user has no sessions
  - [ ] Test when user doesn't exist

- [ ] **cleanup_expired_sessions.py**
  - [ ] Test successful cleanup
  - [ ] Test with no expired sessions
  - [ ] Test with mix of expired and active sessions

- [ ] **list_user_sessions.py**
  - [ ] Test successful listing
  - [ ] Test pagination
  - [ ] Test with no sessions

### Topics Module

- [ ] **create_topic.py**
  - [ ] Test successful creation
  - [ ] Test with tags
  - [ ] Test with invalid data

- [ ] **get_topic_by_id.py**
  - [ ] Test successful retrieval
  - [ ] Test when topic doesn't exist
  - [ ] Test with invalid UUID

- [ ] **update_topic.py**
  - [ ] Test successful update
  - [ ] Test when topic doesn't exist
  - [ ] Test partial updates

- [ ] **delete_topic.py**
  - [ ] Test successful deletion
  - [ ] Test when topic doesn't exist
  - [ ] Test cascading deletion of related records

- [ ] **list_topics.py**
  - [ ] Test successful listing
  - [ ] Test pagination
  - [ ] Test filtering

- [ ] **is_user_topic_author.py**
  - [ ] Test when user is author
  - [ ] Test when user is not author
  - [ ] Test when topic doesn't exist

### Posts Module

- [ ] **create_post.py**
  - [ ] Test successful creation
  - [ ] Test with parent post (reply)
  - [ ] Test with invalid data

- [ ] **get_post_by_id.py**
  - [ ] Test successful retrieval
  - [ ] Test when post doesn't exist
  - [ ] Test with invalid UUID

- [ ] **update_post.py**
  - [ ] Test successful update
  - [ ] Test when post doesn't exist
  - [ ] Test partial updates

- [ ] **delete_post.py**
  - [ ] Test successful deletion
  - [ ] Test when post doesn't exist
  - [ ] Test cascading deletion of related records

- [ ] **list_posts.py**
  - [ ] Test successful listing
  - [ ] Test pagination
  - [ ] Test filtering

- [ ] **list_post_replies.py**
  - [ ] Test successful listing of replies
  - [ ] Test pagination
  - [ ] Test with post that has no replies

- [ ] **get_reply_count.py**
  - [ ] Test with post that has replies
  - [ ] Test with post that has no replies
  - [ ] Test when post doesn't exist

- [ ] **is_user_post_author.py**
  - [ ] Test when user is author
  - [ ] Test when user is not author
  - [ ] Test when post doesn't exist

### Tags Module

- [ ] **create_tag.py**
  - [ ] Test successful creation
  - [ ] Test with duplicate name
  - [ ] Test slug generation

- [ ] **get_tag_by_id.py**
  - [ ] Test successful retrieval
  - [ ] Test when tag doesn't exist
  - [ ] Test with invalid UUID

- [ ] **get_tag_by_name.py**
  - [ ] Test successful retrieval
  - [ ] Test when tag doesn't exist
  - [ ] Test case sensitivity

- [ ] **get_tag_by_slug.py**
  - [ ] Test successful retrieval
  - [ ] Test when tag doesn't exist
  - [ ] Test with invalid slug format

- [ ] **update_tag.py**
  - [ ] Test successful update
  - [ ] Test when tag doesn't exist
  - [ ] Test slug update

- [ ] **delete_tag.py**
  - [ ] Test successful deletion
  - [ ] Test when tag doesn't exist
  - [ ] Test cascading deletion of related records

- [ ] **list_tags.py**
  - [ ] Test successful listing
  - [ ] Test pagination
  - [ ] Test filtering

### Topic Tags Module

- [ ] **create_topic_tag.py**
  - [ ] Test successful creation
  - [ ] Test with duplicate relationship
  - [ ] Test with invalid topic or tag

- [ ] **delete_topic_tag.py**
  - [ ] Test successful deletion
  - [ ] Test when relationship doesn't exist
  - [ ] Test with invalid topic or tag

- [ ] **get_topic_tag.py**
  - [ ] Test successful retrieval
  - [ ] Test when relationship doesn't exist
  - [ ] Test with invalid topic or tag

- [ ] **get_tags_for_topic.py**
  - [ ] Test successful retrieval
  - [ ] Test when topic has no tags
  - [ ] Test when topic doesn't exist

- [ ] **get_topics_for_tag.py**
  - [ ] Test successful retrieval
  - [ ] Test when tag has no topics
  - [ ] Test when tag doesn't exist

- [ ] **add_tags_to_topic.py**
  - [ ] Test successful addition
  - [ ] Test with existing relationships
  - [ ] Test with invalid tags

- [ ] **remove_tags_from_topic.py**
  - [ ] Test successful removal
  - [ ] Test when relationships don't exist
  - [ ] Test with invalid tags

- [ ] **set_topic_tags.py**
  - [ ] Test successful setting
  - [ ] Test replacing existing tags
  - [ ] Test with invalid tags

## Test Template

Here's an improved template for creating tests for db_functions, based on our learnings:

```python
# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db_functions.module.function_name import function_name
from backend.db.models.model_name import ModelName
from backend.schemas.schema_name import SchemaName

@pytest.fixture
def mock_model() -> mock.MagicMock:
    # Create a mock model instance with all required properties
    model = mock.MagicMock(spec=ModelName)
    model.id = uuid.uuid4()
    # Add other properties as needed
    return model

@pytest.fixture
def mock_schema(mock_model) -> SchemaName:
    # Create a schema instance that would be returned by converters
    return SchemaName(
        id=mock_model.id,
        # Add other properties as needed
    )

@pytest.mark.asyncio
async def test_function_success(mock_model, mock_schema) -> None:
    # Arrange
    test_id = mock_model.id

    # Mock the database query - RULE #10 compliance: only operates on its own model
    with (
        mock.patch.object(
            ModelName, "get_or_none", new=mock.AsyncMock(return_value=mock_model)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.module.function_name.converter_function",
            new=mock.AsyncMock(return_value=mock_schema)
        ) as mock_converter
    ):
        # Act
        result = await function_name(test_id)

        # Assert
        assert result is not None
        assert result.id == mock_model.id
        # Add other assertions but skip datetime comparisons

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_converter.assert_called_once_with(mock_model)

@pytest.mark.asyncio
async def test_function_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()

    # Mock the database query
    with mock.patch.object(
        ModelName, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await function_name(test_id)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)

@pytest.mark.asyncio
async def test_function_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        ModelName, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await function_name(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)
```

## Implementation Strategy

1. **Start with Core Functions**: Begin with the most critical functions in the users module
2. **Create Base Fixtures**: Develop reusable fixtures for common models and schemas
3. **Use Proper Mocking**: Use `mock.patch.object` instead of directly assigning to class attributes
4. **Test in Isolation**: Mock all dependencies to test each function in isolation
5. **Test Database Errors**: Always include tests for database connection errors and exceptions
6. **Verify Rule #10**: Explicitly verify that functions only directly operate on their own model
7. **Test Transaction Handling**: For functions that perform multiple operations, test what happens if one operation fails
8. **Skip Datetime Comparisons**: Avoid direct datetime comparisons or use appropriate comparison methods
9. **Track Coverage**: Use pytest-cov to monitor progress on coverage improvements
10. **Fix Lint Issues**: Address import sorting and line length issues in test files

## Next Steps

Based on our progress, the next functions to test in the users module are:

1. `set_user_password.py` - Referenced by `create_user.py` and critical for user management
2. `update_user.py` - Important for user profile management
3. `record_login_success.py` and `record_login_failure.py` - Critical for security tracking

## Commands for Testing

- Run all tests: `just pytest`
- Run tests for a specific module: `cd backend && uv run pytest tests/db_functions/users/`
- Run a specific test: `cd backend && uv run pytest tests/db_functions/users/test_get_user_by_id.py`
- Run with coverage: `cd backend && uv run pytest tests/db_functions/users/ --cov=backend.db_functions.users`
- Check coverage report: `cd backend && uv run pytest tests/db_functions/users/ --cov=backend.db_functions.users --cov-report=term`

## Completion Criteria

- [ ] All db_functions have corresponding test files
- [ ] Each function has tests for success cases, error cases, and edge cases
- [ ] Overall test coverage for db_functions is at least 90%
- [ ] All tests pass consistently
- [ ] Tests verify compliance with RULE #10 (MODEL-SPECIFIC DB FUNCTIONS)
