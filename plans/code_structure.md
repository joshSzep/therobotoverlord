# Code Structure for The Robot Overlord

This document outlines the code organization for The Robot Overlord project, with a particular focus on how database models and API endpoints are structured. This structure emphasizes clarity, maintainability, and a clean separation of concerns.

## Project Structure

The backend follows a hybrid approach combining flat model organization with clear separation of database concerns:

```
backend/
├── migrations/                   # Aerich migration files
│   └── models/                   # App-specific migrations
├── pyproject.toml                # Project configuration with Aerich settings
└── src/backend/
    ├── db/                       # Database-related code
    │   ├── __init__.py           # Database initialization
    │   ├── base.py               # BaseModel definition
    │   ├── config.py             # Database configuration with TORTOISE_ORM
    │   └── models/               # One file per model
    │       ├── __init__.py       # Imports and registers all models
    │       ├── user.py           # User model
    │       ├── user_session.py   # UserSession model
    │       ├── login_attempt.py  # LoginAttempt model
    │       ├── topic.py          # Topic model
    │       ├── post.py           # Post model
    │       ├── tag.py            # Tag model
    │       ├── topic_tag.py      # TopicTag model
    │       ├── ai_analysis.py    # AIAnalysis model
    │       ├── rejection.py      # Rejection model
    │       ├── moderator_action.py # ModeratorAction model
    │       ├── moderator_note.py # ModeratorNote model
    │       ├── user_event.py     # UserEvent model
    │       ├── topic_view.py     # TopicView model
    │       ├── api_usage.py      # APIUsage model
    │       └── audit_log.py      # AuditLog model
    ├── routes/                   # API endpoints by feature
    │   ├── users/                # User-related endpoints
    │   │   ├── __init__.py       # Router setup
    │   │   ├── auth.py           # Authentication endpoints
    │   │   ├── profile.py        # User profile endpoints
    │   │   └── schemas.py        # Pydantic schemas for users
    │   ├── topics/               # Topic-related endpoints
    │   │   ├── __init__.py       # Router setup
    │   │   ├── create.py         # Topic creation endpoints
    │   │   ├── view.py           # Topic viewing endpoints
    │   │   └── schemas.py        # Pydantic schemas for topics
    │   ├── posts/                # Post-related endpoints
    │   │   ├── __init__.py       # Router setup
    │   │   ├── submit.py         # Post submission endpoints
    │   │   ├── moderate.py       # Post moderation endpoints
    │   │   └── schemas.py        # Pydantic schemas for posts
    │   └── admin/                # Admin endpoints
    │       ├── __init__.py       # Router setup
    │       ├── reports.py        # Admin reporting endpoints
    │       └── schemas.py        # Pydantic schemas for admin
    ├── utils/                    # Shared utilities
    │   ├── auth.py               # Authentication utilities
    │   ├── ai_client.py          # AI moderation client
    │   └── datetime.py           # DateTime handling utilities
    └── app.py                    # FastAPI application setup
```

## Key Design Principles

1. **One Model Per File**: Each database model is in its own file for clarity and maintainability.

2. **Database Separation**: All database-related code is contained within the `db` package.

3. **Feature-Based Routes**: API endpoints are organized by feature with clean separation of concerns.

4. **Pydantic Separation**: API models (Pydantic) are separate from database models (Tortoise ORM).

5. **Router Structure**: Each feature has its own router, with `__init__.py` handling router setup.

## Implementation Guidelines

### BaseModel Implementation

```python
# In db/base.py
from tortoise import fields, models
import uuid
from datetime import datetime

class BaseModel(models.Model):
    """Base model for all tables with common fields."""

    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
```

### Individual Model Implementation

Each model should be defined in its own file:

```python
# In db/models/user.py
from backend.db.base import BaseModel
from tortoise import fields

class User(BaseModel):
    """User model with authentication fields."""

    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    display_name = fields.CharField(max_length=100)
    is_verified = fields.BooleanField(default=False)
    verification_token = fields.CharField(max_length=255, null=True)
    last_login = fields.DatetimeField(null=True)
    failed_login_attempts = fields.IntField(default=0)
    role = fields.CharEnumField(
        enum_type=UserRole,  # Define this enum in the same file
        default=UserRole.USER
    )
    is_locked = fields.BooleanField(default=False)

    # Methods for the model...
```

### Model Registration

The `db/models/__init__.py` file should import and register all models:

```python
# In db/models/__init__.py
from backend.db.models.user import User
from backend.db.models.user_session import UserSession
from backend.db.models.login_attempt import LoginAttempt
# Import all other models...

# This list is used for Tortoise ORM registration
models = [
    User,
    UserSession,
    LoginAttempt,
    # All other models...
]

__all__ = [
    "User",
    "UserSession",
    "LoginAttempt",
    # All other model names...
]
```

### Database Configuration with Aerich Support

```python
# In db/config.py
import os
from tortoise import Tortoise
from typing import Dict, Any, Optional

# Database URL from environment variable with fallback
DB_URL = os.getenv("DATABASE_URL", "postgres://username:password@localhost:5432/robotoverlord")

# Aerich-compatible Tortoise config
TORTOISE_ORM: Dict[str, Any] = {
    "connections": {
        "default": DB_URL
    },
    "apps": {
        "models": {
            "models": ["backend.db.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

async def init_db(db_url: Optional[str] = None):
    """Initialize database connection."""
    # Create a copy of the config for runtime use
    config = TORTOISE_ORM.copy()

    # Override connection URL if provided
    if db_url:
        config["connections"]["default"] = db_url

    await Tortoise.init(config=config)

async def close_db():
    """Close database connection."""
    await Tortoise.close_connections()
```

### FastAPI Integration

```python
# In app.py
from fastapi import FastAPI
from backend.db.config import init_db, close_db
from backend.routes.users import router as users_router
from backend.routes.topics import router as topics_router
from backend.routes.posts import router as posts_router
from backend.routes.admin import router as admin_router

app = FastAPI(title="The Robot Overlord")

@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

# Include routers
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(topics_router, prefix="/topics", tags=["topics"])
app.include_router(posts_router, prefix="/posts", tags=["posts"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
```

### Migration Management

We use Aerich for database migrations. This requires additional setup:

1. **pyproject.toml Configuration**:
```toml
[tool.aerich]
tortoise_orm = "backend.db.config.TORTOISE_ORM"
location = "./migrations"
src_folder = "./backend"
```

2. **justfile Commands for Migrations**:
```
db-init:
    cd backend && uv run aerich init-db

db-migrate name:
    cd backend && uv run aerich migrate --name {{name}}

db-migrate-empty name:
    cd backend && uv run aerich migrate --name {{name}} --empty

db-upgrade:
    cd backend && uv run aerich upgrade

db-downgrade:
    cd backend && uv run aerich downgrade

db-history:
    cd backend && uv run aerich history
```

### Feature Router Setup

```python
# In routes/users/__init__.py
from fastapi import APIRouter
from backend.routes.users import auth, profile

router = APIRouter()

# Include routes from feature modules
router.include_router(auth.router, prefix="/auth")
router.include_router(profile.router, prefix="/profile")
```

## Testing Structure

The test directory should mirror the source code structure:

```
backend/tests/
├── conftest.py                   # Pytest fixtures
├── db/
│   ├── models/
│   │   ├── test_user.py
│   │   ├── test_topic.py
│   │   └── ...
│   └── test_config.py
├── routes/
│   ├── users/
│   │   ├── test_auth.py
│   │   └── test_profile.py
│   ├── topics/
│   │   └── ...
│   └── ...
└── utils/
    └── test_auth.py
```

## Implementation Order

1. Base infrastructure (db/base.py, db/config.py)
2. Core user models and authentication
3. Content models (topics, posts)
4. AI moderation models
5. Analytics and audit models
