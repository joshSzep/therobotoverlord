#!/bin/bash

set -e

echo "Starting The Robot Overlord prod backend with Gunicorn..."
cd backend
uv run gunicorn -c gunicorn.conf.py
cd ..
echo "...Stopped The Robot Overlord prod backend with Gunicorn"
