#!/bin/bash
# Test GCP Deployment
# Run from anywhere to test your GCP deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "Testing GCP + TinyLlama Deployment"
echo "=========================================="
echo ""

read -p "Enter your GCP External IP: " GCP_IP

if [ -z "$GCP_IP" ]; then
    echo -e "${RED}Error: IP address required${NC}"
    exit 1
fi

BASE_URL="http://$GCP_IP:8000"

echo -e "${YELLOW}[1/6] Testing Backend Health...${NC}"
HEALTH=$(curl -s "$BASE_URL/api/v1/health" || echo "FAILED")

if [[ $HEALTH == *"ok"* ]]; then
    echo -e "${GREEN}✅ Backend is running${NC}"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo "Response: $HEALTH"
fi
echo ""

echo -e "${YELLOW}[2/6] Testing Database Connection...${NC}"
if [[ $HEALTH == *"database_connected\":true"* ]]; then
    echo -e "${GREEN}✅ Database connected${NC}"
else
    echo -e "${RED}❌ Database not connected${NC}"
fi
echo ""

echo -e "${YELLOW}[3/6] Testing LLM Health...${NC}"
LLM_HEALTH=$(curl -s "$BASE_URL/api/v1/llm/health" || echo "FAILED")

if [[ $LLM_HEALTH == *"ollama_available\":true"* ]]; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
else
    echo -e "${RED}❌ Ollama not accessible${NC}"
fi

if [[ $LLM_HEALTH == *"vector_store_initialized\":true"* ]]; then
    echo -e "${GREEN}✅ Vector store initialized${NC}"
else
    echo -e "${YELLOW}⚠️  Vector store not initialized${NC}"
    echo "Run: curl -X POST $BASE_URL/api/v1/llm/initialize"
fi

echo "$LLM_HEALTH" | python3 -m json.tool 2>/dev/null || echo "$LLM_HEALTH"
echo ""

echo -e "${YELLOW}[4/6] Testing LLM Query...${NC}"
QUERY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/llm/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Hello, are you working?"}' || echo "FAILED")

if [[ $QUERY_RESPONSE == *"answer"* ]]; then
    echo -e "${GREEN}✅ LLM query successful${NC}"
    echo "Response:"
    echo "$QUERY_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$QUERY_RESPONSE"
else
    echo -e "${RED}❌ LLM query failed${NC}"
    echo "Response: $QUERY_RESPONSE"
fi
echo ""

echo -e "${YELLOW}[5/6] Testing Protocols Endpoint...${NC}"
PROTOCOLS=$(curl -s "$BASE_URL/protocols" || echo "FAILED")

if [[ $PROTOCOLS == *"["* ]]; then
    PROTOCOL_COUNT=$(echo "$PROTOCOLS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo -e "${GREEN}✅ Protocols endpoint working${NC}"
    echo "Protocol count: $PROTOCOL_COUNT"
else
    echo -e "${RED}❌ Protocols endpoint failed${NC}"
fi
echo ""

echo -e "${YELLOW}[6/6] Testing API Documentation...${NC}"
DOC_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")

if [ "$DOC_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✅ API docs accessible at: $BASE_URL/docs${NC}"
else
    echo -e "${RED}❌ API docs not accessible${NC}"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""

if [[ $HEALTH == *"ok"* ]] && \
   [[ $LLM_HEALTH == *"ollama_available\":true"* ]] && \
   [[ $QUERY_RESPONSE == *"answer"* ]]; then
    echo -e "${GREEN}✅ All critical tests passed!${NC}"
    echo ""
    echo "Your GCP deployment is working correctly!"
    echo ""
    echo "URLs:"
    echo "- API: $BASE_URL"
    echo "- Docs: $BASE_URL/docs"
    echo "- Health: $BASE_URL/api/v1/health"
    echo "- LLM: $BASE_URL/api/v1/llm/health"
    echo ""
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. SSH into GCP: gcloud compute ssh defi-backend"
    echo "2. Check backend logs: sudo journalctl -u defi-backend -f"
    echo "3. Check Ollama logs: sudo journalctl -u ollama -f"
    echo "4. Test locally on GCP: curl http://localhost:8000/api/v1/health"
    echo ""
fi

