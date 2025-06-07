#!/bin/bash

set -e

PORT=8000

# Kill any processes using port 8000
echo "Checking for processes using port $PORT..."
PID=$(lsof -ti:$PORT)
if [ -n "$PID" ]; then
  echo "Killing process $PID using port $PORT"
  kill -9 $PID
  sleep 1
else
  echo "No processes found using port $PORT"
fi

echo "Starting The Robot Overlord dev backend with uvicorn..."
cd backend
uv run uvicorn src.backend.app:app --reload
cd ..
echo "...Stopped The Robot Overlord dev backend with uvicorn"
