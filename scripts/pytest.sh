#!/bin/bash

set -e

# Set environment to test
export ENVIRONMENT="test"

# Change to backend directory
cd backend

# Clean up any existing test database file
if [ -f "test_db.sqlite3" ]; then
    echo "Removing existing test database..."
    rm test_db.sqlite3
fi

# Run pytest with uv
echo "Running tests with ENVIRONMENT=test..."
uv run pytest "$@"

cd ..
