#!/bin/bash

set -e

echo "=== Starting complete database reset and migration initialization ==="

# Step 1: Drop the existing database
echo "Dropping existing database..."
dropdb robot_overlord || echo "Database does not exist, continuing..."

# Step 2: Remove existing migrations
echo "Removing existing migrations..."
rm -rf backend/migrations/models
mkdir -p backend/migrations/models

# Step 3: Create a new database
echo "Creating new database..."
createdb robot_overlord

# Step 4: Initialize aerich and create initial migration
echo "Initializing aerich..."
cd backend
uv run aerich init -t backend.db.config.TORTOISE_ORM
uv run aerich init-db
cd ..

echo "=== Database reset and migration initialization complete ==="
