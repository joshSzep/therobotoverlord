# Database Migrations with Aerich

This document outlines the migration strategy for The Robot Overlord project using Aerich, a purpose-built migration tool for Tortoise ORM.

## Overview

Aerich provides a way to version control our database schema changes, making it possible to:
- Track all database schema changes in version control
- Apply migrations consistently across development, staging, and production environments
- Roll back changes when necessary
- Collaborate effectively with a team working on the same database schema

## Setup and Configuration

### Directory Structure

```
backend/
├── migrations/           # Migration files directory (created by Aerich)
│   └── models/           # App-specific migrations
├── src/backend/
│   ├── db/
│   │   ├── __init__.py
│   │   ├── config.py     # Contains TORTOISE_ORM config
│   │   ├── base.py
│   │   └── models/
│   │       └── ...
│   └── ...
└── pyproject.toml        # Will contain Aerich configuration
```

### Configuration Files

#### In `db/config.py`:

```python
"""Database configuration for Tortoise ORM."""

import os
from typing import Dict, Any

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
```

#### In `pyproject.toml` (after initialization):

```toml
[tool.aerich]
tortoise_orm = "backend.db.config.TORTOISE_ORM"
location = "./migrations"
src_folder = "./backend"
```

## Migration Workflow

### Initial Setup

1. **Install Aerich**:
   ```bash
   uv pip install "aerich[toml]"
   ```

2. **Initialize Aerich**:
   ```bash
   aerich init -t backend.db.config.TORTOISE_ORM
   ```
   This creates the `migrations` directory and adds configuration to `pyproject.toml`.

3. **Initialize Database**:
   ```bash
   aerich init-db
   ```
   This creates the initial schema in the database and generates a migration file.

### Day-to-Day Development

#### Making Schema Changes

1. **Update your model files** in the `backend/src/backend/db/models/` directory.

2. **Generate migration**:
   ```bash
   aerich migrate --name descriptive_change_name
   ```
   This creates a new migration file in `migrations/models/` with a name like `1_20250524193000_descriptive_change_name.py`.

3. **Apply migration**:
   ```bash
   aerich upgrade
   ```
   This applies any pending migrations to bring the database up to date.

#### Advanced Use Cases

1. **Creating empty migrations** (for custom SQL or complex changes):
   ```bash
   aerich migrate --name custom_change --empty
   ```
   Then edit the generated file to add your custom migration logic.

2. **Rolling back migrations**:
   ```bash
   aerich downgrade  # Rolls back one migration
   aerich downgrade -v 2  # Rolls back to version 2
   ```

3. **Viewing migration history**:
   ```bash
   aerich history
   ```

4. **Viewing pending migrations**:
   ```bash
   aerich heads
   ```

## Special Considerations

### Column Renames

When Aerich detects a potential column rename, it will prompt:
```
Rename {old_column} to {new_column} [True]
```

- **True**: Perform a rename operation (preserves data)
- **False**: Drop the old column and create a new one (loses data)

### Multiple Databases

If we need to support multiple databases in the future, we would:

1. Add additional connections to the TORTOISE_ORM config
2. Specify the app when running migrations:
   ```bash
   aerich --app other_models migrate
   ```

### Handling Migration Conflicts

When working in a team, migration conflicts may occur if multiple developers make schema changes simultaneously. To resolve:

1. Pull the latest code from version control
2. Run `aerich heads` to see available migrations
3. Apply migrations with `aerich upgrade`
4. Make your new changes and generate a new migration

## Integration with CI/CD

### CI Checks

Add these steps to your CI pipeline:

```yaml
- name: Check for unapplied migrations
  run: uv run aerich heads | grep -q "^$" || (echo "Error: Unapplied migrations found" && exit 1)
```

### Deployment Process

1. **Pre-deployment**:
   - Backup the database
   - Run migration check

2. **During deployment**:
   ```bash
   uv run aerich upgrade
   ```

3. **Post-deployment**:
   - Verify application functionality
   - Have rollback plan ready if needed

## justfile Commands

Add these commands to the project's `justfile` for convenience:

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

db-heads:
    cd backend && uv run aerich heads
```

## Best Practices

1. **Migration Naming**: Use descriptive names for migrations (e.g., `add_user_verification` rather than `update`)

2. **Small, Focused Migrations**: Create separate migrations for logically distinct changes

3. **Testing Migrations**: Test migrations on a copy of production data before deploying

4. **Backup Before Migrating**: Always back up the database before applying migrations in production

5. **Version Control**: Always commit migration files to version control along with model changes

6. **Migration Reviews**: Have team members review migration files during code review

7. **Documentation**: Document complex migrations with comments in the migration file

8. **Avoid Raw SQL**: Use Tortoise ORM's schema modification methods when possible instead of raw SQL

9. **Handle Data Migrations**: For complex data migrations, consider creating a separate script or using an empty migration
