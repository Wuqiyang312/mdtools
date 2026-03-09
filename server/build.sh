#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$SCRIPT_DIR"

echo "✓ Python server - no build required"
echo ""
echo "To start the server:"
echo "  cd $PROJECT_DIR && ./server/run.sh"
echo ""
echo "Or with custom port:"
echo "  PORT=3000 ./server/run.sh"
echo ""
echo "Or directly:"
echo "  python3 server/server.py --port 8080"
