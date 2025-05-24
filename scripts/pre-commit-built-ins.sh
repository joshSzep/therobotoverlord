#!/bin/bash

set -e

cd backend
uv run pre-commit run check-merge-conflict --all-files
uv run pre-commit run detect-private-key --all-files
uv run pre-commit run end-of-file-fixer --all-files
uv run pre-commit run trailing-whitespace --all-files
cd ..
