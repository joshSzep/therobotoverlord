# Content Structure Implementation Checklist

This checklist outlines the steps to implement the core content structure for The Robot Overlord debate platform, including Topics, Tags, and Posts.

## Database Models

### Topic Model
- [ ] Create `Topic` model in `backend/db/models/topic.py`
  - [ ] Implement fields:
    - [ ] `title`: String
    - [ ] `author`: ForeignKey(User)
    - [ ] `description`: Text (optional)
  - [ ] Inherit from BaseModel (UUID4 PK, created_at, updated_at)

### Tag Model
- [ ] Create `Tag` model in `backend/db/models/tag.py`
  - [ ] Implement fields:
    - [ ] `name`: String (unique)
    - [ ] `slug`: String (unique)
  - [ ] Inherit from BaseModel
  - [ ] Add slug generation logic

### TopicTag Model
- [ ] Create `TopicTag` model in `backend/db/models/topic_tag.py`
  - [ ] Implement fields:
    - [ ] `topic`: ForeignKey(Topic)
    - [ ] `tag`: ForeignKey(Tag)
  - [ ] Inherit from BaseModel
  - [ ] Add unique constraint for topic+tag combination

### Post Model
- [ ] Create `Post` model in `backend/db/models/post.py`
  - [ ] Implement fields:
    - [ ] `content`: Text
    - [ ] `author`: ForeignKey(User)
    - [ ] `topic`: ForeignKey(Topic)
    - [ ] `parent_post`: ForeignKey(Post, nullable) - For threaded replies
  - [ ] Inherit from BaseModel
  - [ ] Add validation to ensure parent_post belongs to same topic

## API Endpoints

### Topics API
- [ ] Create topics feature module in `backend/routes/topics/`
  - [ ] Create `__init__.py` with router setup
  - [ ] Create `models.py` with Pydantic schemas:
    - [ ] `TopicCreate`
    - [ ] `TopicResponse`
    - [ ] `TopicList`
  - [ ] Create CRUD endpoints in `topics.py`:
    - [ ] `GET /topics/` - List all topics
    - [ ] `POST /topics/` - Create a new topic
    - [ ] `GET /topics/{topic_id}` - Get a specific topic
    - [ ] `PUT /topics/{topic_id}` - Update a topic
    - [ ] `DELETE /topics/{topic_id}` - Delete a topic

### Tags API
- [ ] Create tags feature module in `backend/routes/tags/`
  - [ ] Create `__init__.py` with router setup
  - [ ] Create `models.py` with Pydantic schemas:
    - [ ] `TagCreate`
    - [ ] `TagResponse`
    - [ ] `TagList`
  - [ ] Create CRUD endpoints in `tags.py`:
    - [ ] `GET /tags/` - List all tags
    - [ ] `POST /tags/` - Create a new tag
    - [ ] `GET /tags/{tag_id}` - Get a specific tag
    - [ ] `PUT /tags/{tag_id}` - Update a tag
    - [ ] `DELETE /tags/{tag_id}` - Delete a tag

### Posts API
- [ ] Create posts feature module in `backend/routes/posts/`
  - [ ] Create `__init__.py` with router setup
  - [ ] Create `models.py` with Pydantic schemas:
    - [ ] `PostCreate`
    - [ ] `PostResponse`
    - [ ] `PostList`
    - [ ] `PostUpdate`
  - [ ] Create CRUD endpoints in `posts.py`:
    - [ ] `GET /posts/` - List posts (with topic filter)
    - [ ] `POST /posts/` - Create a new post
    - [ ] `GET /posts/{post_id}` - Get a specific post
    - [ ] `PUT /posts/{post_id}` - Update a post
    - [ ] `DELETE /posts/{post_id}` - Delete a post
  - [ ] Create threaded view endpoints:
    - [ ] `GET /topics/{topic_id}/posts/` - Get all top-level posts for a topic
    - [ ] `GET /posts/{post_id}/replies/` - Get all replies to a post

## Database Migrations

- [ ] Create migration for new models:
  - [ ] Run `aerich migrate` to generate migration
  - [ ] Review migration file
  - [ ] Run `aerich upgrade` to apply migration

## Tests

### Model Tests
- [ ] Create tests for Topic model
- [ ] Create tests for Tag model
- [ ] Create tests for TopicTag model
- [ ] Create tests for Post model

### API Tests
- [ ] Create tests for Topics API endpoints
- [ ] Create tests for Tags API endpoints
- [ ] Create tests for Posts API endpoints
- [ ] Create tests for threaded post functionality

## Integration

- [ ] Register all routers in `app.py`
- [ ] Ensure proper error handling
- [ ] Implement authentication/authorization checks
- [ ] Add models to Tortoise ORM config in `db/config.py`

## Documentation

- [ ] Update API documentation with new endpoints
- [ ] Add example requests/responses

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
