#!/bin/bash

set -e

echo "Downgrading database with aerich..."
cd backend
uv run aerich downgrade
cd ..
echo "...Finished downgrading database"
