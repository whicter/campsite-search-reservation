#!/bin/bash

# Campsite Search - Start RQ Worker

echo "⚙️  Starting RQ Worker..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Kill existing RQ workers
if pgrep -f "rq worker" > /dev/null; then
    echo -e "${YELLOW}⚠️  Stopping existing RQ workers...${NC}"
    pkill -f "rq worker" 2>/dev/null
    sleep 2
fi

# Check if Redis is running
if ! brew services list | grep redis | grep started > /dev/null; then
    echo -e "${RED}❌ Redis is not running!${NC}"
    echo "Please run: ./start_infrastructure.sh first"
    exit 1
fi

echo -e "${GREEN}✅ Redis is ready${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Starting RQ Worker (monitoring queue)"
echo "🔍 Redis: redis://localhost:6379/0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Required for macOS to prevent fork() issues
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Start RQ Worker in foreground
PATH="$(pwd)/campsite-env/bin:$PATH" ./campsite-env/bin/rq worker monitoring --url redis://localhost:6379/0
