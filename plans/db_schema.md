# Database Schema for The Robot Overlord

This document outlines the database schema design for The Robot Overlord debate platform using Tortoise ORM.

## Base Model

All models will inherit from a common base model with these fields:

```
BaseModel
- id: UUID4 (PK)
- created_at: DateTime (UTC)
- updated_at: DateTime (UTC)
- deleted_at: DateTime (UTC, nullable) - For soft deletion
```

## Core Models

### User Management

The user system needs to track authentication data, security information, and role-based permissions:

```
User
- email: String (unique)
- password_hash: String
- display_name: String
- is_verified: Boolean
- verification_token: String (nullable)
- last_login: DateTime (nullable)
- failed_login_attempts: Integer
- role: Enum (user, moderator, admin)
- is_locked: Boolean
```

**Security Tracking**:
```
UserSession
- user: ForeignKey(User)
- ip_address: String
- user_agent: String
- session_token: String
- expires_at: DateTime
- is_active: Boolean
```

**Login Attempts**:
```
LoginAttempt
- user: ForeignKey(User, nullable) - Can be null for failed attempts with non-existent users
- ip_address: String
- user_agent: String
- success: Boolean
- timestamp: DateTime
```

### Content Structure

The core content structure for the debate platform:

```
Topic
- title: String
- author: ForeignKey(User)
- description: Text (optional)
```

```
Tag
- name: String (unique)
- slug: String (unique)
```

```
TopicTag
- topic: ForeignKey(Topic)
- tag: ForeignKey(Tag)
```

```
Post
- content: Text
- author: ForeignKey(User)
- topic: ForeignKey(Topic)
- parent_post: ForeignKey(Post, nullable) - For threaded replies
```

### AI Moderation

The AI moderation pipeline will be complex and may evolve over time:

```
AIAnalysis
- post: ForeignKey(Post)
- model_version: String
- raw_response: JSON
- is_approved: Boolean
- decision_reason: Text
- processing_time_ms: Integer
- processing_cost: Decimal (nullable)
```

```
Rejection
- ai_analysis: OneToOneField(AIAnalysis)
- rejection_type: String  # e.g., "hate_speech", "logical_fallacy"
- explanation: Text
```

**Considerations for Future AI Pipeline Development**:
- We may need to support multiple analyses per post (different models or re-analysis)
- A queue system for pending analyses might be necessary
- Error handling for AI service failures
- Tracking retries and analysis history
- Supporting A/B testing between different moderation models

### Moderation Features

Support for manual moderation by authorized users:

```
ModeratorAction
- post: ForeignKey(Post)
- moderator: ForeignKey(User)
- action_type: Enum (reject, restore)
- reason: Text
- previous_status: Boolean - The previous approval status
```

```
ModeratorNote
- user: ForeignKey(User) - The user being noted about
- moderator: ForeignKey(User) - The moderator making the note
- content: Text
- is_warning: Boolean
```

### User Engagement and Analytics

Comprehensive event tracking for user engagement:

```
UserEvent
- user: ForeignKey(User, nullable) - Can be null for anonymous events
- event_type: String  # e.g., "view_topic", "create_post", "login"
- ip_address: String (nullable)
- user_agent: String (nullable)
- resource_type: String (nullable)  # e.g., "topic", "post"
- resource_id: UUID (nullable)  # ID of the related resource
- metadata: JSON (nullable)  # Additional event-specific data
```

```
TopicView
- topic: ForeignKey(Topic)
- user: ForeignKey(User, nullable) - Can be null for anonymous views
- ip_address: String
- user_agent: String
- timestamp: DateTime
- session_id: String (nullable)
```

### System Administration

Tracking API usage and administrative actions:

```
APIUsage
- endpoint: String
- method: String
- user: ForeignKey(User, nullable)
- ip_address: String
- response_time_ms: Integer
- status_code: Integer
- timestamp: DateTime
```

```
AuditLog
- user: ForeignKey(User)
- action: String
- resource_type: String
- resource_id: UUID
- old_values: JSON (nullable)
- new_values: JSON (nullable)
- metadata: JSON (nullable)
```

## Design Principles and Considerations

1. **Fully Normalized Schema**: The MVP prioritizes a well-designed, normalized schema. Performance optimizations will be addressed later if needed.

2. **UUID Primary Keys**: All models use UUID4 for primary keys for security and simplicity.

3. **Timezone Awareness**: All datetime fields are stored in UTC timezone.

4. **Calculated Fields**: Approval/rejection counters are calculated dynamically rather than stored.

5. **Comprehensive Event Tracking**: We track detailed user events for analytics and security purposes.

6. **Audit Logging**: All significant administrative actions are logged for accountability.

7. **Soft Deletion**: We use a deleted_at timestamp rather than hard deletion for data integrity.

8. **Security-First Design**: Login attempts, session tracking, and IP monitoring are built in from the start.

9. **Extensible AI Pipeline**: The schema is designed to accommodate future enhancements to the AI moderation system.

10. **Tags vs. Categories**: We use a tagging system for flexible content organization rather than rigid categories.
