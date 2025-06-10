# Unit Test Coverage Improvement Plan

**Current Coverage:** 61.76% (2028/5303 lines uncovered)
**Target Coverage:** 80%+
**Priority:** Focus on critical business logic and 0% coverage files first

## Phase 1: Critical Priority (0% Coverage Files)

### Files with 0% Coverage - Immediate Action Required

- [x] **src/backend/db_functions/posts/find_post_by_content.py** (32 lines, 0% coverage)
  - [x] Test post content search functionality
  - [x] Test edge cases (empty content, special characters)
  - [x] Test performance with large datasets

- [x] **src/backend/db_functions/posts/get_post_by_pending_post_id.py** (23 lines, 0% coverage)
  - [x] Test successful post retrieval
  - [x] Test non-existent pending post ID
  - [x] Test database connection errors

- [x] **src/backend/db_functions/user_sessions/create_user_session.py** (20 lines, 0% coverage)
  - [x] Test session creation with valid user
  - [x] Test session creation with invalid user
  - [x] Test session token generation

- [x] **src/backend/routes/pending_posts/moderate_pending_post.py** (28 lines, 0% coverage)
  - [x] Test moderation approval flow
  - [x] Test moderation rejection flow
  - [x] Test unauthorized access

- [x] **src/backend/routes/profile/list_my_rejected_posts.py** (10 lines, 0% coverage)
  - [x] Test rejected posts listing for authenticated user
  - [x] Test empty results
  - [x] Test pagination

- [x] **src/backend/routes/user_stats/get_user_stats_by_id.py** (12 lines, 0% coverage)
  - [x] Test user stats retrieval
  - [x] Test non-existent user
  - [x] Test stats calculation accuracy

- [x] **src/backend/routes/html/home/index.py** (20 lines, 0% coverage)
  - [x] Test home page rendering
  - [x] Test authenticated vs unauthenticated views

- [x] **src/backend/dominate_templates/topics/list.py** (80 lines, 0% coverage)
  - [x] Test topic template rendering
  - [x] Test template with various data scenarios

- [x] **src/backend/utils/moderation_config.py** (11 lines, 0% coverage)
  - [x] Test moderation configuration loading
  - [x] Test default values
  - [x] Test configuration validation

## Phase 2: High Priority (Very Low Coverage <30%)

### Template Files (Low Priority but Easy Wins)
- [x] **src/backend/dominate_templates/base.py** (37% coverage)
  - [x] Test base template rendering
  - [x] Test template inheritance

- [x] **src/backend/dominate_templates/components/pagination.py** (16% coverage)
  - [x] Test pagination component with various page counts
  - [x] Test edge cases (page 1, last page)

- [x] **src/backend/dominate_templates/home.py** (22% coverage)
  - [x] Test home template with different user states
  - [x] Test with and without topics and posts

### Database Functions
- [x] **src/backend/db_functions/posts/find_post_from_pending_post.py** (29% coverage)
  - [x] Test post matching logic
  - [x] Test duplicate detection

- [ ] **src/backend/db_functions/user_sessions/delete_user_session.py** (25% coverage)
  - [ ] Test session deletion
  - [ ] Test cascade effects

### Utility Functions
- [ ] **src/backend/utils/thread_builder.py** (16% coverage)
  - [ ] Test thread building logic
  - [ ] Test nested thread structures

- [ ] **src/backend/utils/auth.py** (31% coverage)
  - [ ] Test authentication middleware
  - [ ] Test token validation
  - [ ] Test permission checks

## Phase 3: Medium Priority (30-60% Coverage)

### AI/Moderation Components
- [ ] **src/backend/tasks/ai_moderation_task.py** (35% coverage)
  - [ ] Test AI moderation task execution
  - [ ] Test error handling in moderation pipeline

- [ ] **src/backend/db_functions/pending_posts/approve_and_create_post.py** (42% coverage)
  - [ ] Test approval workflow
  - [ ] Test post creation from pending post

- [ ] **src/backend/db_functions/pending_posts/list_pending_posts.py** (42% coverage)
  - [ ] Test pending posts listing with filters
  - [ ] Test sorting and pagination

### Route Handlers
- [ ] **src/backend/routes/api/posts/create_pending_post.py** (53% coverage)
  - [ ] Test API endpoint for creating pending posts
  - [ ] Test validation and error responses

- [ ] **src/backend/routes/html/posts/create_reply.py** (48% coverage)
  - [ ] Test reply creation form handling
  - [ ] Test reply validation

## Phase 4: Converter Functions (Quick Wins)

### Schema Converters (Easy to test, high impact)
- [ ] **src/backend/converters/pending_post_to_schema.py** (57% coverage)
  - [ ] Test pending post schema conversion
  - [ ] Test with various pending post states

- [ ] **src/backend/converters/rejected_post_to_schema.py** (57% coverage)
  - [ ] Test rejected post schema conversion

- [ ] **src/backend/converters/user_event_to_schema.py** (30% coverage)
  - [ ] Test user event schema conversion
  - [ ] Test different event types

- [ ] **src/backend/converters/user_schema_to_response.py** (57% coverage)
  - [ ] Test user response schema conversion

## Phase 5: Integration and E2E Scenarios

### Critical User Flows
- [ ] **Authentication Flow Tests**
  - [ ] Complete login/logout cycle
  - [ ] Password change flow
  - [ ] Session management

- [ ] **Post Creation and Moderation Flow**
  - [ ] Create post → pending → approval → published
  - [ ] Create post → pending → rejection → rejected

- [ ] **Topic and Tag Management**
  - [ ] Topic creation with tags
  - [ ] Tag association and removal

## Testing Strategy Guidelines

### For Each Test File:
1. **Happy Path Tests** - Normal operation scenarios
2. **Edge Case Tests** - Boundary conditions, empty inputs
3. **Error Handling Tests** - Database errors, validation failures
4. **Security Tests** - Unauthorized access, input sanitization
5. **Performance Tests** - Large datasets, concurrent operations

### Test Patterns to Follow:
- Use existing test patterns from high-coverage files
- Mock external dependencies (database, AI services)
- Test both success and failure scenarios
- Include parametrized tests for multiple input scenarios
- Add integration tests for critical workflows

### Coverage Targets by Phase:
- **Phase 1 Completion:** ~70% total coverage
- **Phase 2 Completion:** ~75% total coverage
- **Phase 3 Completion:** ~80% total coverage
- **Phase 4 Completion:** ~85% total coverage

## Notes:
- Focus on business-critical functionality first
- Template files are lower priority but easy wins
- Consider adding integration tests alongside unit tests
- Review and update existing tests that may be outdated
- Use pytest fixtures effectively to reduce test setup duplication
