#!/bin/bash

# Production deployment script for SafeFi DeFi Risk Assessment
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting SafeFi Deployment${NC}"

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo -e "${RED}❌ .env.production file not found${NC}"
    echo "Creating .env.production from template..."
    cp .env.production.example .env.production 2>/dev/null || cp ../env.example .env.production
    echo -e "${YELLOW}⚠️  Please update .env.production with your configuration${NC}"
    exit 1
fi

# Load environment variables
set -a
source .env.production
set +a

# Variables
TAG=${1:-latest}
REGISTRY=${REGISTRY:-ghcr.io/safefi}
COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${YELLOW}📦 Pulling latest images...${NC}"
docker-compose -f $COMPOSE_FILE pull

echo -e "${YELLOW}🏗️  Building services...${NC}"
docker-compose -f $COMPOSE_FILE up -d

echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 15

echo -e "${YELLOW}🔍 Running database migrations...${NC}"
docker-compose -f $COMPOSE_FILE exec -T api alembic upgrade head || echo "No migrations to run"

echo -e "${YELLOW}✅ Health checks...${NC}"

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    docker-compose -f $COMPOSE_FILE logs api
    exit 1
fi

# Check frontend health
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${RED}✗ Frontend health check failed${NC}"
    docker-compose -f $COMPOSE_FILE logs frontend
    exit 1
fi

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo "Services are now available at:"
echo "  - Frontend: http://localhost"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - MLflow: http://localhost:5000"
echo ""
echo "To view logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "To stop: docker-compose -f $COMPOSE_FILE down"
