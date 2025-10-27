#!/bin/bash

# Test deployment script for SafeFi
# This script tests the Docker setup locally

set -e

echo "🧪 Testing SafeFi Docker Deployment"
echo "=================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose is installed${NC}"

# Build and start services
echo ""
echo "🔨 Building Docker images..."
docker-compose build --no-cache

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 20

# Health checks
echo ""
echo "🏥 Running health checks..."

# Check frontend
if curl -f -s http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${RED}✗ Frontend health check failed${NC}"
fi

# Check backend
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
fi

# Check database
if docker exec safefi-db pg_isready -U defi_user > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database is healthy${NC}"
else
    echo -e "${RED}✗ Database health check failed${NC}"
fi

# Check MLflow
if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MLflow is healthy${NC}"
else
    echo -e "${RED}✗ MLflow health check failed${NC}"
fi

# Test API endpoints
echo ""
echo "🔍 Testing API endpoints..."

# Test root endpoint
if curl -f -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API root endpoint responding${NC}"
else
    echo -e "${RED}✗ API root endpoint failed${NC}"
fi

# Test protocols endpoint
if curl -f -s http://localhost:8000/api/v1/protocols?limit=1 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API protocols endpoint responding${NC}"
else
    echo -e "${YELLOW}⚠ API protocols endpoint failed (may need data)${NC}"
fi

# Summary
echo ""
echo "📊 Summary"
echo "==========="
echo "Services are now running:"
echo "  - Frontend: http://localhost"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - MLflow: http://localhost:5000"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo -e "${GREEN}✅ Deployment test completed!${NC}"
