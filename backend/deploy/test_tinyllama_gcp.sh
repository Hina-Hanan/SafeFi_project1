#!/bin/bash
# TinyLlama Test Script for GCP
# Tests all LLM endpoints to verify deployment

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default to localhost, or use provided IP
API_URL="${1:-http://localhost:8000}"

echo -e "${BLUE}=========================================="
echo "TinyLlama Test Suite"
echo "==========================================${NC}"
echo ""
echo "Testing API at: $API_URL"
echo ""

# Test 1: Backend Health
echo -e "${BLUE}[Test 1/6] Backend Health Check...${NC}"
if curl -sf "$API_URL/api/v1/health" > /dev/null; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
    curl -s "$API_URL/api/v1/health" | python3 -m json.tool
else
    echo -e "${RED}✗ FAILED: Backend not responding${NC}"
    exit 1
fi
echo ""

# Test 2: LLM Health
echo -e "${BLUE}[Test 2/6] LLM Health Check...${NC}"
if curl -sf "$API_URL/api/v1/llm/health" > /dev/null; then
    echo -e "${GREEN}✓ LLM is healthy${NC}"
    curl -s "$API_URL/api/v1/llm/health" | python3 -m json.tool
else
    echo -e "${RED}✗ FAILED: LLM endpoint not responding${NC}"
    exit 1
fi
echo ""

# Test 3: Simple Query
echo -e "${BLUE}[Test 3/6] Testing simple query...${NC}"
RESPONSE=$(curl -s -X POST "$API_URL/api/v1/llm/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Hello, are you working?"}')
  
if [ -n "$RESPONSE" ]; then
    echo -e "${GREEN}✓ Query works${NC}"
    echo "$RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}✗ FAILED: Query endpoint not working${NC}"
    exit 1
fi
echo ""

# Test 4: Protocol Query
echo -e "${BLUE}[Test 4/6] Testing protocol information query...${NC}"
curl -s -X POST "$API_URL/api/v1/llm/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"What protocols are monitored?"}' | python3 -m json.tool
echo -e "${GREEN}✓ Protocol query completed${NC}"
echo ""

# Test 5: Risk Query
echo -e "${BLUE}[Test 5/6] Testing risk analysis query...${NC}"
curl -s -X POST "$API_URL/api/v1/llm/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Which protocols have high risk scores?"}' | python3 -m json.tool
echo -e "${GREEN}✓ Risk query completed${NC}"
echo ""

# Test 6: Context Retrieval
echo -e "${BLUE}[Test 6/6] Testing context retrieval...${NC}"
curl -s "$API_URL/api/v1/llm/context/Uniswap?top_k=3" | python3 -m json.tool
echo -e "${GREEN}✓ Context retrieval works${NC}"
echo ""

echo -e "${BLUE}=========================================="
echo -e "${GREEN}All Tests Passed!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${GREEN}Your TinyLlama setup is working correctly!${NC}"
echo ""
echo "Try these queries:"
echo "  - What protocols are monitored?"
echo "  - Which protocols have high risk?"
echo "  - Tell me about Uniswap risk level"
echo "  - What protocol has the highest TVL?"
echo "  - How does the risk scoring work?"
echo ""


