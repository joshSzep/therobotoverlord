#!/bin/bash

set -e

# Run tests with coverage
cd backend
uv run pytest --cov=backend --cov-report=xml --cov-report=html --cov-report=term
cd ..
