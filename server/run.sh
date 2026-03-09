#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

PORT=${PORT:-8080}

echo "Starting server on port $PORT..."
python3 "$SCRIPT_DIR/server.py" --port $PORT
