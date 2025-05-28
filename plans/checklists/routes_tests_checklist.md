# Routes Tests Checklist

## Overview
This checklist tracks the implementation status of tests for all route endpoints in the Robot Overlord project.

## Testing Guidelines
- Each test file should follow the naming convention `test_[route_name].py`
- Use `@pytest.mark.asyncio` for testing async route handlers
- Mock all database dependencies
- Test both success and failure scenarios
- Verify appropriate status codes and response formats

## Implementation Status

### Profile Routes (High Priority)
- [x] `get_me.py`
  - [x] Test successful profile retrieval
  - [x] Test unauthorized access
- [x] `change_password.py`
  - [x] Test successful password change
  - [x] Test with incorrect current password
  - [x] Test with invalid new password
  - [x] Test unauthorized access
- [x] `logout.py`
  - [x] Test successful logout
  - [x] Test with multiple sessions
  - [x] Test with no matching sessions

### Topics Routes (High Priority)
- [x] `create_topic.py`
  - [x] Test successful topic creation
  - [x] Test with existing tag
  - [x] Test with tag error
- [x] `get_topic.py`
  - [x] Test successful topic retrieval
  - [x] Test with non-existent topic
- [x] `list_topics.py`
  - [x] Test successful listing
  - [x] Test with pagination
  - [x] Test with filters
- [x] `update_topic.py`
  - [x] Test successful update
  - [x] Test with non-existent topic
  - [x] Test unauthorized access
- [x] `delete_topic.py`
  - [x] Test successful deletion
  - [x] Test with non-existent topic
  - [x] Test unauthorized access
- [x] `add_topic_tag.py`
  - [x] Test successful tag addition
  - [x] Test with non-existent topic
  - [x] Test with non-existent tag
  - [x] Test tag already associated with topic
- [x] `list_topic_posts.py`
  - [x] Test successful listing
  - [x] Test with non-existent topic
  - [x] Test with pagination

### Auth Routes (Medium Priority)
- [ ] `login.py`
  - [ ] Test successful login
  - [ ] Test with invalid credentials
  - [ ] Test with inactive user
- [ ] `register.py`
  - [ ] Test successful registration
  - [ ] Test with existing email
  - [ ] Test with invalid data
- [x] `refresh_token.py` (Already implemented)

### Tags Routes (Medium Priority)
- [ ] `create_tag.py`
  - [ ] Test successful tag creation
  - [ ] Test with invalid data
  - [ ] Test unauthorized access
  - [ ] Test with duplicate name
- [ ] `get_tag.py`
  - [ ] Test successful tag retrieval
  - [ ] Test with non-existent tag
- [ ] `update_tag.py`
  - [ ] Test successful update
  - [ ] Test with non-existent tag
  - [ ] Test unauthorized access
- [ ] `delete_tag.py`
  - [ ] Test successful deletion
  - [ ] Test with non-existent tag
  - [ ] Test unauthorized access
- [x] `list_tags.py` (Already implemented)

### Posts Routes (Low Priority)
- [x] `create_post.py` (Already implemented)
- [x] `get_post.py` (Already implemented)
- [x] `list_posts.py` (Already implemented)
- [x] `list_post_replies.py` (Already implemented)
- [ ] `update_post.py`
  - [ ] Test successful update
  - [ ] Test with non-existent post
  - [ ] Test unauthorized access
  - [ ] Test when user is not author
- [ ] `delete_post.py`
  - [ ] Test successful deletion
  - [ ] Test with non-existent post
  - [ ] Test unauthorized access
  - [ ] Test when user is not author

## Test Template Structure

```python
# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from fastapi import HTTPException

# Project-specific imports
from backend.routes.[category].[route_name] import [route_function]
from backend.schemas.[entity] import [relevant_schemas]

@pytest.mark.asyncio
async def test_[route_name]_success():
    """Test successful [operation]."""
    # Arrange
    # Set up test data and mocks

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.[category].[route_name].[dependency]",
            new=mock.AsyncMock(return_value=[mock_response]),
        ),
    ):
        # Act
        result = await [route_function]([params])

        # Assert
        assert [expected_conditions]

@pytest.mark.asyncio
async def test_[route_name]_error_case():
    """Test [operation] with [error condition]."""
    # Arrange
    # Set up test data and mocks

    # Mock dependencies to simulate error
    with (
        mock.patch(
            "backend.routes.[category].[route_name].[dependency]",
            new=mock.AsyncMock(side_effect=[exception]),
        ),
    ):
        # Act & Assert
        with pytest.raises([ExceptionType]) as excinfo:
            await [route_function]([params])

        # Verify exception details
        assert excinfo.value.status_code == [expected_status_code]
        assert [expected_message] in excinfo.value.detail
```

## Progress Tracking
- Total routes: 26
- Routes with tests: 12 (46%)
- Routes without tests: 14 (54%)

## Implementation Notes
- Focus on one route category at a time to maintain context
- Ensure adherence to project rules, especially Rule #2 (one route per file) and Rule #4 (trailing slashes in routes)
- Remember to update this checklist as tests are implemented
