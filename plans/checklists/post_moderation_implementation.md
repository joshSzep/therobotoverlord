# Post Moderation Implementation Checklist

## Backend Database Functions

- [x] **Update Post Creation Flow**
  - [x] Modify `create_post_action` to use `create_pending_post` instead of `create_post`
  - [x] Add background task to trigger AI moderation after pending post creation
  - [x] Update reply creation to use pending posts system

- [x] **Enhance AI Moderation Service**
  - [x] Configure Anthropic Claude API integration
  - [x] Improve moderation prompts for better content analysis
  - [x] Add more sophisticated rejection criteria beyond simple keywords
  - [x] Implement confidence threshold settings for auto-approval/rejection

- [x] **User Stats Tracking**
  - [x] Update user approval counter when post is approved
  - [x] Update user rejection counter when post is rejected
  - [x] Create user event entries for post approvals and rejections

## API Routes

- [x] **HTML Routes for Pending Posts**
  - [x] Create route to view user's own pending posts
  - [x] Create route to view user's rejected posts with feedback
  - [x] Add admin routes for manual moderation of pending posts
  - [x] Fix router prefixes to avoid double prefixing with /html

- [x] **REST API Updates**
  - [x] Update post creation endpoint to use pending posts workflow
  - [x] Add endpoints for checking post moderation status
  - [x] Create webhook for moderation completion notifications

## Frontend/Templates (Dominate templates)

- [x] **User Interface Updates**
  - [x] Add pending post indicator in user profile
  - [x] Create pending posts list view
  - [x] Create rejected posts list view with feedback
  - [x] Add moderation status indicators on posts

- [x] **Feedback Display**
  - [x] Design Soviet-style feedback messages for rejected posts
  - [x] Create UI component for displaying moderation feedback
  - [ ] Add highlighting for newly approved posts

## Configuration

- [x] **Settings Management**
  - [x] Add configuration for `AI_MODERATION_ENABLED`
  - [x] Add configuration for `AI_MODERATION_AUTO_APPROVE`
  - [x] Add configuration for `AI_MODERATION_AUTO_REJECT`
  - [x] Add configuration for confidence thresholds

- [x] **API Keys and Security**
  - [x] Set up secure storage for Anthropic API keys
  - [x] Implement rate limiting for moderation requests
  - [x] Add logging for moderation decisions

## Testing

- [ ] **Unit Tests**
  - [ ] Test pending post creation
  - [ ] Test moderation pipeline
  - [ ] Test approval and rejection flows
  - [ ] Test user stats updates

- [ ] **Integration Tests**
  - [ ] Test end-to-end post submission and moderation
  - [ ] Test moderation feedback display
  - [ ] Test user profile stats updates

## Documentation

- [ ] **Developer Documentation**
  - [ ] Document moderation pipeline architecture
  - [ ] Document AI moderation service configuration
  - [ ] Document database schema changes

- [ ] **User Documentation**
  - [ ] Create help text explaining the moderation process
  - [ ] Add tooltips for moderation status indicators
  - [ ] Write guidelines for post submission

## Deployment

- [ ] **Database Migrations**
  - [ ] Create migration for any schema changes
  - [ ] Test migration on staging environment

- [x] **Feature Flags**
  - [x] Add feature flag for enabling/disabling moderation
  - [ ] Add gradual rollout capability

## Future Enhancements

- [ ] **Advanced Moderation Features**
  - [ ] Implement user reputation system affecting moderation strictness
  - [ ] Add appeals process for rejected posts
  - [x] Create moderation dashboard for admins
  - [ ] Implement batch moderation capabilities
