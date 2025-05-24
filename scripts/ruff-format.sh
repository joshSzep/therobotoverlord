#!/bin/bash

set -e

cd backend
uv run ruff format
cd ..
