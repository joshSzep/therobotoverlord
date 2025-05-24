#!/bin/bash

set -e

# Verify that pre-commit hooks are installed and pass
cd backend
uv run pre-commit run --all
cd ..
