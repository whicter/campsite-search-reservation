#!/bin/bash

# Start Frontend Script
# This script starts the React development server

echo "🚀 Starting Campsite Search Frontend..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Dependencies not installed!"
    echo "Please run: yarn install"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Start the development server
echo "✅ Starting React development server on http://localhost:3000"
echo "Press CTRL+C to stop"
echo ""

yarn start
