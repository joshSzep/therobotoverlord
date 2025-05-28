#!/bin/bash

set -e

echo "Starting The Robot Overlord test backend with uvicorn..."
cd backend

# Create a timestamp for the backup filename
TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
BACKUP_FILE=".env.$TIMESTAMP.backup"

# Stash the original .env file if it exists
if [ -f .env ]; then
  echo "Stashing original .env file to $BACKUP_FILE..."
  cp .env "$BACKUP_FILE"
fi

# Use the test environment
cp .env.test .env

# Trap to restore the original .env file on exit
function cleanup {
  if [ -f "$BACKUP_FILE" ]; then
    echo "Restoring original .env file from $BACKUP_FILE..."
    cp "$BACKUP_FILE" .env
    rm "$BACKUP_FILE"
  fi
  cd ..
  echo "...Stopped The Robot Overlord test backend with uvicorn"
}
trap cleanup EXIT

# Run the server
uv run uvicorn src.backend.app:app --reload
