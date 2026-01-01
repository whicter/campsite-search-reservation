#!/bin/bash

# Campsite Search - Stop Services Script

echo "🛑 Stopping Campsite Search Services..."
echo ""

# Kill FastAPI server
lsof -ti:8000 > /dev/null 2>&1 && echo "Stopping API server..." && lsof -ti:8000 | xargs kill -9 2>/dev/null

# Kill RQ worker
pkill -f "rq worker" 2>/dev/null && echo "Stopping RQ worker..."

sleep 1

echo ""
echo "✅ All services stopped!"
echo ""
