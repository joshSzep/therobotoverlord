# Post Moderation Implementation Checklist

## Backend Database Functions

- [x] **Update Post Creation Flow**
  - [x] Modify `create_post_action` to use `create_pending_post` instead of `create_post`
  - [x] Add background task to trigger AI moderation after pending post creation
  - [x] Update reply creation to use pending posts system

- [ ] **Enhance AI Moderation Service**
  - [ ] Configure Anthropic Claude API integration
  - [ ] Improve moderation prompts for better content analysis
  - [ ] Add more sophisticated rejection criteria beyond simple keywords
  - [ ] Implement confidence threshold settings for auto-approval/rejection

- [ ] **User Stats Tracking**
  - [ ] Update user approval counter when post is approved
  - [ ] Update user rejection counter when post is rejected
  - [ ] Create user event entries for post approvals and rejections

## API Routes

- [ ] **HTML Routes for Pending Posts**
  - [ ] Create route to view user's own pending posts
  - [ ] Create route to view user's rejected posts with feedback
  - [ ] Add admin routes for manual moderation of pending posts

- [ ] **REST API Updates**
  - [ ] Update post creation endpoint to use pending posts workflow
  - [ ] Add endpoints for checking post moderation status
  - [ ] Create webhook for moderation completion notifications

## Frontend/Templates

- [ ] **User Interface Updates**
  - [ ] Add pending post indicator in user profile
  - [ ] Create pending posts list view
  - [ ] Create rejected posts list view with feedback
  - [ ] Add moderation status indicators on posts

- [ ] **Feedback Display**
  - [ ] Design Soviet-style feedback messages for rejected posts
  - [ ] Create UI component for displaying moderation feedback
  - [ ] Add highlighting for newly approved posts

## Configuration

- [ ] **Settings Management**
  - [ ] Add configuration for `AI_MODERATION_ENABLED`
  - [ ] Add configuration for `AI_MODERATION_AUTO_APPROVE`
  - [ ] Add configuration for `AI_MODERATION_AUTO_REJECT`
  - [ ] Add configuration for confidence thresholds

- [ ] **API Keys and Security**
  - [ ] Set up secure storage for Anthropic API keys
  - [ ] Implement rate limiting for moderation requests
  - [ ] Add logging for moderation decisions

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

- [ ] **Feature Flags**
  - [ ] Add feature flag for enabling/disabling moderation
  - [ ] Add gradual rollout capability

## Future Enhancements

- [ ] **Advanced Moderation Features**
  - [ ] Implement user reputation system affecting moderation strictness
  - [ ] Add appeals process for rejected posts
  - [ ] Create moderation dashboard for admins
  - [ ] Implement batch moderation capabilities
