#!/bin/bash

set -e

# Install backend dependencies
cd backend
uv sync
uv run pre-commit install
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
