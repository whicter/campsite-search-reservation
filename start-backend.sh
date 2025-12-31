#!/bin/bash

# Start Backend Script
# This script activates the virtual environment and starts the FastAPI backend

echo "🚀 Starting Campsite Search Backend..."

cd backend

# Check if virtual environment exists
if [ ! -d "campsite-env" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv campsite-env"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source campsite-env/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

# Start the server
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "Press CTRL+C to stop"
echo ""

python -m app.main
