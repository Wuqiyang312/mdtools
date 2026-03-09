#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

echo "Starting with docker-compose..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✓ Server started"
    echo ""
    echo "To stop:"
    echo "  docker-compose down"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
else
    echo "✗ Failed to start"
    exit 1
fi
