#!/bin/bash

set -e

cd backend
uv run pyright
cd ..
