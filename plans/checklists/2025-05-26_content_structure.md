# Content Structure Implementation Checklist

This checklist outlines the steps to implement the core content structure for The Robot Overlord debate platform, including Topics, Tags, and Posts.

## Database Models

### Topic Model
- [x] Create `Topic` model in `backend/db/models/topic.py`
  - [x] Implement fields:
    - [x] `title`: String
    - [x] `author`: ForeignKey(User)
    - [x] `description`: Text (optional)
  - [x] Inherit from BaseModel (UUID4 PK, created_at, updated_at)

### Tag Model
- [x] Create `Tag` model in `backend/db/models/tag.py`
  - [x] Implement fields:
    - [x] `name`: String (unique)
    - [x] `slug`: String (unique)
  - [x] Inherit from BaseModel
  - [x] Add slug generation logic

### TopicTag Model
- [x] Create `TopicTag` model in `backend/db/models/topic_tag.py`
  - [x] Implement fields:
    - [x] `topic`: ForeignKey(Topic)
    - [x] `tag`: ForeignKey(Tag)
  - [x] Inherit from BaseModel
  - [x] Add unique constraint for topic+tag combination

### Post Model
- [x] Create `Post` model in `backend/db/models/post.py`
  - [x] Implement fields:
    - [x] `content`: Text
    - [x] `author`: ForeignKey(User)
    - [x] `topic`: ForeignKey(Topic)
    - [x] `parent_post`: ForeignKey(Post, nullable) - For threaded replies
  - [x] Inherit from BaseModel
  - [x] Add validation to ensure parent_post belongs to same topic

## API Endpoints

### Topics API
- [x] Create topics feature module in `backend/routes/topics/`
  - [x] Create `__init__.py` with router setup
  - [x] Create `models.py` with Pydantic schemas:
    - [x] `TopicCreate`
    - [x] `TopicResponse`
    - [x] `TopicList`
  - [x] Create CRUD endpoints in `topics.py`:
    - [x] `GET /topics/` - List all topics
    - [x] `POST /topics/` - Create a new topic
    - [x] `GET /topics/{topic_id}` - Get a specific topic
    - [x] `PUT /topics/{topic_id}` - Update a topic
    - [x] `DELETE /topics/{topic_id}` - Delete a topic

### Tags API
- [x] Create tags feature module in `backend/routes/tags/`
  - [x] Create `__init__.py` with router setup
  - [x] Create `schemas.py` with Pydantic schemas:
    - [x] `TagCreate`
    - [x] `TagResponse`
    - [x] `TagList`
  - [x] Create CRUD endpoints in `tags.py`:
    - [x] `GET /tags/` - List all tags
    - [x] `POST /tags/` - Create a new tag
    - [x] `GET /tags/{tag_id}` - Get a specific tag
    - [x] `PUT /tags/{tag_id}` - Update a tag
    - [x] `DELETE /tags/{tag_id}` - Delete a tag

### Posts API
- [x] Create posts feature module in `backend/routes/posts/`
  - [x] Create `__init__.py` with router setup
  - [x] Create `schemas.py` with Pydantic schemas:
    - [x] `PostCreate`
    - [x] `PostResponse`
    - [x] `PostList`
    - [x] `PostUpdate`
  - [x] Create CRUD endpoints in `posts.py`:
    - [x] `GET /posts/` - List posts (with topic filter)
    - [x] `POST /posts/` - Create a new post
    - [x] `GET /posts/{post_id}` - Get a specific post
    - [x] `PUT /posts/{post_id}` - Update a post
    - [x] `DELETE /posts/{post_id}` - Delete a post
  - [x] Create threaded view endpoints:
    - [x] `GET /topics/{topic_id}/posts/` - Get all top-level posts for a topic
    - [x] `GET /posts/{post_id}/replies/` - Get all replies to a post

## Database Migrations

- [x] Create migration for new models:
  - [x] Run `aerich migrate` to generate migration
  - [x] Review migration file
  - [x] Run `aerich upgrade` to apply migration

## Tests

### Model Tests
- [x] Create tests for Topic model
- [x] Create tests for Tag model
- [x] Create tests for TopicTag model
- [x] Create tests for Post model

### API Tests
- [x] Create tests for Topics API endpoints
- [x] Create tests for Tags API endpoints
- [x] Create tests for Posts API endpoints
- [x] Create tests for threaded post functionality

## Integration

- [x] Register all routers in `app.py`
- [x] Ensure proper error handling
- [x] Implement authentication/authorization checks
- [x] Add models to Tortoise ORM config in `db/config.py`

## Documentation

- [x] Update API documentation with new endpoints
- [x] Add example requests/responses

## Manual Testing Checklist

- [ ] Create a new topic
- [ ] Add tags to a topic
- [ ] Create a top-level post in a topic
- [ ] Create a reply to an existing post
- [ ] List all topics
- [ ] List all posts in a topic
- [ ] List all replies to a post
- [ ] Update a post
- [ ] Delete a post
- [ ] Verify thread structure is maintained
