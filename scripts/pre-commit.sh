#!/bin/bash

set -e

cd backend
uv run pre-commit run --all-files
cd ..
