#!/bin/bash

# Campsite Search - Stop Services Script

echo "🛑 Stopping Campsite Search Services..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kill FastAPI server
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}Stopping API server...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
else
    echo "API server is not running"
fi

# Kill RQ worker
if pgrep -f "rq worker" > /dev/null; then
    echo -e "${YELLOW}Stopping RQ worker...${NC}"
    pkill -f "rq worker" 2>/dev/null
else
    echo "RQ worker is not running"
fi

sleep 1

echo ""
echo -e "${GREEN}✅ Application services stopped!${NC}"
echo ""
echo "💡 PostgreSQL 和 Redis 仍在后台运行"
echo "   如需停止："
echo "   brew services stop postgresql@15"
echo "   brew services stop redis"
echo ""
