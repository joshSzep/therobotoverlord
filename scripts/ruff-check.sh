#!/bin/bash

set -e

cd backend
uv run ruff check --fix
cd ..
