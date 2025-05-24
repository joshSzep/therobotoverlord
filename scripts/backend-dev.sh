#!/bin/bash

set -e

echo "Starting The Robot Overlord dev backend with uvicorn..."
cd backend
uv run uvicorn src.backend.app:app --reload
cd ..
echo "...Stopped The Robot Overlord dev backend with uvicorn"
