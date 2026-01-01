#!/bin/bash

# Campsite Search - Start FastAPI Server

echo "🚀 Starting FastAPI Server..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if port 8000 is in use
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 8000 is in use. Stopping existing process...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Check if PostgreSQL is running
if ! brew services list | grep postgresql@15 | grep started > /dev/null; then
    echo -e "${RED}❌ PostgreSQL is not running!${NC}"
    echo "Please run: ./start_infrastructure.sh first"
    exit 1
fi

# Check if Redis is running
if ! brew services list | grep redis | grep started > /dev/null; then
    echo -e "${RED}❌ Redis is not running!${NC}"
    echo "Please run: ./start_infrastructure.sh first"
    exit 1
fi

echo -e "${GREEN}✅ Infrastructure services are ready${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 Starting FastAPI on http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start FastAPI in foreground
PATH="$(pwd)/campsite-env/bin:$PATH" ./campsite-env/bin/python -m app.main
