#!/bin/bash
# Test script for DisplayPack 2.0 Simulator

echo "=== DisplayPack 2.0 Simulator - Quick Test ==="
echo ""

# Check if files exist
echo "Checking files..."
if [ -f "basic_server.py" ]; then
    echo "✓ basic_server.py found"
else
    echo "✗ basic_server.py NOT found"
    exit 1
fi

if [ -f "client.html" ]; then
    echo "✓ client.html found"
else
    echo "⚠ client.html not found (will use embedded fallback)"
fi

if [ -f "bounce.bas" ]; then
    echo "✓ bounce.bas found"
else
    echo "⚠ bounce.bas not found"
fi

echo ""
echo "=== Starting server with bouncing ball demo ==="
echo ""
echo "1. Server will start on http://localhost:8080"
echo "2. Open that URL in your browser"
echo "3. You should see a bouncing red ball"
echo "4. Press Ctrl+C in this terminal to stop"
echo ""
echo "Starting in 3 seconds..."
sleep 3

python3 basic_server.py bounce.bas --run
