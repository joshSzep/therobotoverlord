#!/bin/bash

set -e

cd backend
uv run mypy .
cd ..
