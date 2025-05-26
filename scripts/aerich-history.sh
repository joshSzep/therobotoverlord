#!/bin/bash

set -e

echo "Showing migration history with aerich..."
cd backend
uv run aerich history
cd ..
echo "...Finished showing migration history"
