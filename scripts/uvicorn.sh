#!/bin/bash

# Don't exit on error
set +e

PORT=8000

# Check for processes using port 8000
echo "Checking for processes using port $PORT..."

# Find processes using the port without using a pipe
PROCESSES=$(lsof -ti:$PORT 2>/dev/null)

# Check if any processes were found
if [ -n "$PROCESSES" ]; then
  echo "Found processes using port $PORT: $PROCESSES"
  # Kill each process individually
  for PID in $PROCESSES; do
    echo "Killing process $PID"
    kill -9 $PID 2>/dev/null || true
  done
  sleep 1
else
  echo "No processes found using port $PORT"
fi

echo "Starting The Robot Overlord dev backend with uvicorn..."
cd backend
uv run uvicorn src.backend.app:app --reload
cd ..
echo "...Stopped The Robot Overlord dev backend with uvicorn"
