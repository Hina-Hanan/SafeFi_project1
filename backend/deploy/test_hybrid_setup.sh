#!/bin/bash
# Test Hybrid Setup
# Run this from anywhere to test your deployment

set -e

echo "=========================================="
echo "Testing Hybrid Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get GCP IP
read -p "Enter your GCP instance IP: " GCP_IP

echo ""
echo -e "${YELLOW}[1/6] Testing GCP Backend Health...${NC}"
HEALTH_RESPONSE=$(curl -s http://$GCP_IP:8000/api/v1/health || echo "FAILED")

if [[ $HEALTH_RESPONSE == *"ok"* ]]; then
    echo -e "${GREEN}✓ Backend is running${NC}"
    echo $HEALTH_RESPONSE | jq '.' 2>/dev/null || echo $HEALTH_RESPONSE
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    echo "Response: $HEALTH_RESPONSE"
fi

echo ""
echo -e "${YELLOW}[2/6] Testing Database Connection...${NC}"
if [[ $HEALTH_RESPONSE == *"database_connected\":true"* ]]; then
    echo -e "${GREEN}✓ Database connected${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
fi

echo ""
echo -e "${YELLOW}[3/6] Testing LLM Assistant Health...${NC}"
LLM_HEALTH=$(curl -s http://$GCP_IP:8000/api/v1/llm/health || echo "FAILED")

if [[ $LLM_HEALTH == *"ollama_available\":true"* ]]; then
    echo -e "${GREEN}✓ Ollama is accessible from GCP${NC}"
else
    echo -e "${RED}✗ Ollama connection failed${NC}"
    echo "Response: $LLM_HEALTH"
fi

echo $LLM_HEALTH | jq '.' 2>/dev/null || echo $LLM_HEALTH

echo ""
echo -e "${YELLOW}[4/6] Testing Vector Store...${NC}"
if [[ $LLM_HEALTH == *"vector_store_initialized\":true"* ]]; then
    echo -e "${GREEN}✓ Vector store initialized${NC}"
else
    echo -e "${YELLOW}! Vector store not initialized${NC}"
    echo "Initialize with: curl -X POST http://$GCP_IP:8000/api/v1/llm/initialize"
fi

echo ""
echo -e "${YELLOW}[5/6] Testing LLM Query...${NC}"
QUERY_RESPONSE=$(curl -s -X POST http://$GCP_IP:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, are you working?", "top_k": 3}' || echo "FAILED")

if [[ $QUERY_RESPONSE == *"answer"* ]]; then
    echo -e "${GREEN}✓ LLM query successful${NC}"
    echo "Response:"
    echo $QUERY_RESPONSE | jq '.answer' 2>/dev/null || echo $QUERY_RESPONSE
else
    echo -e "${RED}✗ LLM query failed${NC}"
    echo "Response: $QUERY_RESPONSE"
fi

echo ""
echo -e "${YELLOW}[6/6] Testing Protocols Endpoint...${NC}"
PROTOCOLS_RESPONSE=$(curl -s http://$GCP_IP:8000/protocols || echo "FAILED")

if [[ $PROTOCOLS_RESPONSE == *"["* ]]; then
    PROTOCOL_COUNT=$(echo $PROTOCOLS_RESPONSE | jq '. | length' 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ Protocols endpoint working${NC}"
    echo "Protocol count: $PROTOCOL_COUNT"
else
    echo -e "${RED}✗ Protocols endpoint failed${NC}"
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""

if [[ $HEALTH_RESPONSE == *"ok"* ]] && \
   [[ $LLM_HEALTH == *"ollama_available\":true"* ]] && \
   [[ $QUERY_RESPONSE == *"answer"* ]]; then
    echo -e "${GREEN}✓ All critical tests passed!${NC}"
    echo ""
    echo "Your hybrid deployment is working correctly!"
    echo ""
    echo "Backend URL: http://$GCP_IP:8000"
    echo "API Docs: http://$GCP_IP:8000/docs"
    echo ""
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check GCP backend logs: sudo journalctl -u defi-backend -f"
    echo "2. Verify Ollama URL in GCP .env file"
    echo "3. Test Ollama connectivity from GCP: curl \$OLLAMA_BASE_URL"
    echo "4. Ensure local Ollama is running: curl http://localhost:11434"
    echo ""
fi

echo "Full documentation: markdowns/HYBRID_DEPLOYMENT_GCP.md"
echo ""


