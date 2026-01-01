#!/bin/bash

# Campsite Search - Start Services Script

echo "🚀 Starting Campsite Search Services..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
echo "📋 Checking PostgreSQL..."
if brew services list | grep postgresql@15 | grep started > /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠️  Starting PostgreSQL...${NC}"
    brew services start postgresql@15
fi

echo ""
echo "📋 Checking Redis..."
if brew services list | grep redis | grep started > /dev/null; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠️  Starting Redis...${NC}"
    brew services start redis
fi

echo ""
echo "🔍 Checking ports..."

# Kill old processes
lsof -ti:8000 > /dev/null 2>&1 && echo "Cleaning up port 8000..." && lsof -ti:8000 | xargs kill -9 2>/dev/null
pkill -f "rq worker" 2>/dev/null && echo "Cleaning up RQ worker..."

sleep 2

echo ""
echo "🚀 Starting services..."

# Start FastAPI in background
echo "Starting FastAPI server..."
./campsite-env/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/api_server.log 2>&1 &
API_PID=$!
echo "  → API Server PID: $API_PID"

# Wait for API to start
sleep 3

# Start RQ Worker in background
echo "Starting RQ Worker..."
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES ./campsite-env/bin/rq worker monitoring --url redis://localhost:6379/0 > logs/rq_worker.log 2>&1 &
WORKER_PID=$!
echo "  → RQ Worker PID: $WORKER_PID"

sleep 2

echo ""
echo -e "${GREEN}🎉 All services started!${NC}"
echo ""
echo "Service endpoints:"
echo "  📡 API: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo "  📊 API Logs: tail -f logs/api_server.log"
echo "  ⚙️  Worker Logs: tail -f logs/rq_worker.log"
echo ""
echo "To stop services:"
echo "  ./stop_services.sh"
echo ""
