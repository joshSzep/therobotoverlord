# Route Refactoring Checklist

## Overview
This checklist outlines the steps needed to refactor the existing route files to follow **RULE #2: ONE ROUTE PER FILE** as specified in LLM_RULES.md.

## Posts Routes Refactoring
- [ ] Create a new directory structure for posts routes:
  - [ ] Create `/backend/src/backend/routes/posts/__init__.py` (if not exists)
  - [ ] Create `/backend/src/backend/routes/posts/list.py` for `list_posts`
  - [ ] Create `/backend/src/backend/routes/posts/create.py` for `create_post`
  - [ ] Create `/backend/src/backend/routes/posts/get.py` for `get_post`
  - [ ] Create `/backend/src/backend/routes/posts/update.py` for `update_post`
  - [ ] Create `/backend/src/backend/routes/posts/delete.py` for `delete_post`
  - [ ] Create `/backend/src/backend/routes/posts/list_topic.py` for `list_topic_posts`
  - [ ] Create `/backend/src/backend/routes/posts/list_replies.py` for `list_post_replies`
- [ ] Update `/backend/src/backend/routes/posts/__init__.py` to include all routes
- [ ] Delete the original `/backend/src/backend/routes/posts/posts.py` file

## Topics Routes Refactoring
- [ ] Create a new directory structure for topics routes:
  - [ ] Create `/backend/src/backend/routes/topics/__init__.py` (if not exists)
  - [ ] Create `/backend/src/backend/routes/topics/list.py` for `list_topics`
  - [ ] Create `/backend/src/backend/routes/topics/create.py` for `create_topic`
  - [ ] Create `/backend/src/backend/routes/topics/get.py` for `get_topic`
  - [ ] Create `/backend/src/backend/routes/topics/update.py` for `update_topic`
  - [ ] Create `/backend/src/backend/routes/topics/delete.py` for `delete_topic`
- [ ] Update `/backend/src/backend/routes/topics/__init__.py` to include all routes
- [ ] Delete the original `/backend/src/backend/routes/topics/topics.py` file

## Tags Routes Refactoring
- [ ] Create a new directory structure for tags routes:
  - [ ] Create `/backend/src/backend/routes/tags/__init__.py` (if not exists)
  - [ ] Create `/backend/src/backend/routes/tags/list.py` for `list_tags`
  - [ ] Create `/backend/src/backend/routes/tags/create.py` for `create_tag`
  - [ ] Create `/backend/src/backend/routes/tags/get.py` for `get_tag`
  - [ ] Create `/backend/src/backend/routes/tags/update.py` for `update_tag`
  - [ ] Create `/backend/src/backend/routes/tags/delete.py` for `delete_tag`
- [ ] Update `/backend/src/backend/routes/tags/__init__.py` to include all routes
- [ ] Delete the original `/backend/src/backend/routes/tags/tags.py` file

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
   - [ ] Ensure all tests still pass after refactoring
   - [ ] Update any tests that directly import from the original files

## Example Implementation
For a single route file (e.g., `/backend/src/backend/routes/posts/list.py`):

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

from backend.routes.posts.list import router as list_router
from backend.routes.posts.create import router as create_router
from backend.routes.posts.get import router as get_router
from backend.routes.posts.update import router as update_router
from backend.routes.posts.delete import router as delete_router
from backend.routes.posts.list_topic import router as list_topic_router
from backend.routes.posts.list_replies import router as list_replies_router

router = APIRouter(tags=["posts"])

router.include_router(list_router)
router.include_router(create_router)
router.include_router(get_router)
router.include_router(update_router)
router.include_router(delete_router)
router.include_router(list_topic_router)
router.include_router(list_replies_router)
```
