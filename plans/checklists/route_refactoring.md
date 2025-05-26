# Route Refactoring Checklist

## Overview
This checklist outlines the steps needed to refactor the existing route files to follow **RULE #2: ONE ROUTE PER FILE** as specified in LLM_RULES.md.

## Posts Routes Refactoring
- [x] Create a new directory structure for posts routes:
  - [x] Create `/backend/src/backend/routes/posts/__init__.py` (if not exists)
  - [x] Create `/backend/src/backend/routes/posts/list_posts.py` for `list_posts`
  - [x] Create `/backend/src/backend/routes/posts/create_post.py` for `create_post`
  - [x] Create `/backend/src/backend/routes/posts/get_post.py` for `get_post`
  - [x] Create `/backend/src/backend/routes/posts/update_post.py` for `update_post`
  - [x] Create `/backend/src/backend/routes/posts/delete_post.py` for `delete_post`
  - [x] Create `/backend/src/backend/routes/posts/list_topic_posts.py` for `list_topic_posts`
  - [x] Create `/backend/src/backend/routes/posts/list_post_replies.py` for `list_post_replies`
- [x] Update `/backend/src/backend/routes/posts/__init__.py` to include all routes
- [x] Delete the original `/backend/src/backend/routes/posts/posts.py` file

## Topics Routes Refactoring
- [x] Create a new directory structure for topics routes:
  - [x] Create `/backend/src/backend/routes/topics/__init__.py` (if not exists)
  - [x] Create `/backend/src/backend/routes/topics/list_topics.py` for `list_topics`
  - [x] Create `/backend/src/backend/routes/topics/create_topic.py` for `create_topic`
  - [x] Create `/backend/src/backend/routes/topics/get_topic.py` for `get_topic`
  - [x] Create `/backend/src/backend/routes/topics/update_topic.py` for `update_topic`
  - [x] Create `/backend/src/backend/routes/topics/delete_topic.py` for `delete_topic`
- [x] Update `/backend/src/backend/routes/topics/__init__.py` to include all routes
- [x] Delete the original `/backend/src/backend/routes/topics/topics.py` file

## Tags Routes Refactoring
- [x] Create a new directory structure for tags routes:
  - [x] Create `/backend/src/backend/routes/tags/__init__.py` (if not exists)
  - [x] Create `/backend/src/backend/routes/tags/list_tags.py` for `list_tags`
  - [x] Create `/backend/src/backend/routes/tags/create_tag.py` for `create_tag`
  - [x] Create `/backend/src/backend/routes/tags/get_tag.py` for `get_tag`
  - [x] Create `/backend/src/backend/routes/tags/update_tag.py` for `update_tag`
  - [x] Create `/backend/src/backend/routes/tags/delete_tag.py` for `delete_tag`
- [x] Update `/backend/src/backend/routes/tags/__init__.py` to include all routes
- [x] Delete the original `/backend/src/backend/routes/tags/tags.py` file

## Implementation Guidelines
1. Each route file should:
   - Import only the dependencies needed for that specific route
   - Define a single router with a single endpoint
   - Export that router for inclusion in the `__init__.py` file

2. Each `__init__.py` file should:
   - Import all individual routers
   - Create a main router for the feature
   - Include all individual routers in the main router
   - Export the main router

3. Testing:
   - [x] Ensure all tests still pass after refactoring
   - [x] Update any tests that directly import from the original files

## Example Implementation
For a single route file (e.g., `/backend/src/backend/routes/posts/list_posts.py`):

```python
# Standard library imports
from typing import Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Query

# Project-specific imports
from backend.db.models.post import Post
from backend.routes.posts.schemas import PostList
from backend.routes.posts.schemas import PostResponse

router = APIRouter()

@router.get("/", response_model=PostList)
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    topic_id: Optional[UUID] = None,
    author_id: Optional[UUID] = None,
) -> PostList:
    # Implementation...
```

For the `__init__.py` file:

```python
from fastapi import APIRouter

from backend.routes.posts.list_posts import router as list_posts_router
from backend.routes.posts.create_post import router as create_post_router
from backend.routes.posts.get_post import router as get_post_router
from backend.routes.posts.update_post import router as update_post_router
from backend.routes.posts.delete_post import router as delete_post_router
from backend.routes.posts.list_topic_posts import router as list_topic_posts_router
from backend.routes.posts.list_post_replies import router as list_post_replies_router

router = APIRouter(tags=["posts"])

router.include_router(list_posts_router)
router.include_router(create_post_router)
router.include_router(get_post_router)
router.include_router(update_post_router)
router.include_router(delete_post_router)
router.include_router(list_topic_posts_router)
router.include_router(list_post_replies_router)
```
