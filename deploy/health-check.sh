#!/bin/bash

# Health check script for SafeFi services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 Running health checks for SafeFi services...${NC}"

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name is healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ $name health check failed${NC}"
        return 1
    fi
}

# Check services
failed=0

echo -e "\n📊 Frontend Health"
if ! check_service "Frontend" "http://localhost/health"; then
    failed=1
fi

echo -e "\n📊 Backend API Health"
if ! check_service "Backend API" "http://localhost:8000/health"; then
    failed=1
fi

echo -e "\n📊 Backend API Info"
if curl -f -s "http://localhost:8000/" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API is responding${NC}"
else
    echo -e "${RED}✗ Backend API is not responding${NC}"
    failed=1
fi

echo -e "\n📊 Database Connection"
if docker exec safefi-db pg_isready -U defi_user > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database is accessible${NC}"
else
    echo -e "${RED}✗ Database health check failed${NC}"
    failed=1
fi

echo -e "\n📊 MLflow Health"
if curl -f -s "http://localhost:5000/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MLflow is accessible${NC}"
else
    echo -e "${RED}✗ MLflow health check failed${NC}"
    failed=1
fi

if [ $failed -eq 0 ]; then
    echo -e "\n${GREEN}✅ All health checks passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some health checks failed${NC}"
    exit 1
fi
