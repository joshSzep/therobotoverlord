#!/bin/bash

set -e

cd backend
uv run pytest
cd ..
