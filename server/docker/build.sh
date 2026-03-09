#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")/.."

cd "$SCRIPT_DIR"

echo "Building Docker image..."
docker build -t mdtools-server -f Dockerfile ../..

if [ $? -eq 0 ]; then
    echo "✓ Docker image built successfully"
    echo ""
    echo "To run:"
    echo "  docker run -p 8080:8080 mdtools-server"
    echo ""
    echo "Or with data volume:"
    echo "  docker run -p 8080:8080 -v \$(pwd)/data:/app/data mdtools-server"
else
    echo "✗ Docker build failed"
    exit 1
fi
