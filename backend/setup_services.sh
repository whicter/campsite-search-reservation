#!/bin/bash

# Campsite Search - Service Setup Script

echo "🚀 Setting up Campsite Search services..."
echo ""

# Colors for output
RED='\033[0.31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo -e "${RED}❌ Homebrew is not installed${NC}"
    echo "Please install Homebrew first: https://brew.sh"
    exit 1
fi

echo -e "${GREEN}✅ Homebrew found${NC}"

# Install PostgreSQL
echo ""
echo "📦 Installing PostgreSQL..."
if ! command -v psql &> /dev/null; then
    brew install postgresql@15
    echo -e "${GREEN}✅ PostgreSQL installed${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL already installed${NC}"
fi

# Install Redis
echo ""
echo "📦 Installing Redis..."
if ! command -v redis-server &> /dev/null; then
    brew install redis
    echo -e "${GREEN}✅ Redis installed${NC}"
else
    echo -e "${YELLOW}⚠️  Redis already installed${NC}"
fi

# Start services
echo ""
echo "🔄 Starting services..."
brew services start postgresql@15
brew services start redis
sleep 2

# Create database
echo ""
echo "🗄️  Creating database..."
if psql postgres -c '' 2>/dev/null; then
    createdb campsite_db 2>/dev/null || echo -e "${YELLOW}⚠️  Database 'campsite_db' may already exist${NC}"
    echo -e "${GREEN}✅ Database ready${NC}"
else
    echo -e "${RED}❌ Could not connect to PostgreSQL${NC}"
    echo "Try running: brew services restart postgresql@15"
    exit 1
fi

# Test Redis
echo ""
echo "🔍 Testing Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not responding${NC}"
    echo "Try running: brew services restart redis"
    exit 1
fi

# Generate secret key
echo ""
echo "🔐 Generating secret key..."
SECRET_KEY=$(openssl rand -hex 32)

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3002

# Database
DATABASE_URL=postgresql://localhost/campsite_db
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists (not modified)${NC}"
    echo "Please add these lines if missing:"
    echo "  DATABASE_URL=postgresql://localhost/campsite_db"
    echo "  REDIS_URL=redis://localhost:6379/0"
    echo "  SECRET_KEY=$SECRET_KEY"
fi

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. cd backend"
echo "  2. ./campsite-env/bin/alembic init alembic"
echo "  3. ./campsite-env/bin/alembic upgrade head"
echo ""
echo "To start the services:"
echo "  Terminal 1: ./campsite-env/bin/uvicorn app.main:app --reload"
echo "  Terminal 2: ./campsite-env/bin/rq worker"
echo "  Terminal 3: cd ../frontend && yarn start"
