#!/bin/bash

# Campsite Search - Start Infrastructure Services (PostgreSQL & Redis)

echo "🚀 Starting Infrastructure Services (PostgreSQL & Redis)..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check and start PostgreSQL
echo "📋 Checking PostgreSQL..."
if brew services list | grep postgresql@15 | grep started > /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠️  Starting PostgreSQL...${NC}"
    brew services start postgresql@15
    sleep 2
fi

echo ""
echo "📋 Checking Redis..."
if brew services list | grep redis | grep started > /dev/null; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠️  Starting Redis...${NC}"
    brew services start redis
    sleep 2
fi

echo ""
echo -e "${GREEN}🎉 Infrastructure services started!${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📍 Next Steps - Start Application Services:${NC}"
echo ""
echo "请打开两个终端窗口，分别运行："
echo ""
echo -e "${BLUE}终端 1 - FastAPI Server:${NC}"
echo "  cd $(pwd)"
echo "  ./start_api.sh"
echo ""
echo -e "${BLUE}终端 2 - RQ Worker:${NC}"
echo "  cd $(pwd)"
echo "  ./start_worker.sh"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "💡 提示：这样可以避免 camply 输出格式问题，并且可以实时看到日志"
echo ""
