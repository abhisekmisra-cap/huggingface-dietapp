#!/bin/bash

echo "==============================================="
echo "   Diet Plan Generator - Web Interface"
echo "==============================================="
echo
echo "Starting the web application..."
echo "Open your browser and go to: http://localhost:5000"
echo
echo "Press Ctrl+C to stop the server"
echo

# Check if virtual environment exists
if [ -f ".venv/bin/python" ]; then
    echo "Using virtual environment..."
    .venv/bin/python app.py
else
    echo "Using system Python..."
    python3 app.py
fi