#!/bin/bash

set -e

# Run tests with coverage
cd backend
uv run pytest
cd ..
