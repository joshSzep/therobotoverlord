#!/bin/bash

set -e

echo "Upgrading database with aerich..."
cd backend
uv run aerich upgrade
cd ..
echo "...Finished upgrading database"
