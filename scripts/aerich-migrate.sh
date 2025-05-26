#!/bin/bash

set -e

echo "Creating a new migration with aerich..."
cd backend
uv run aerich migrate
cd ..
echo "...Finished creating migration"
