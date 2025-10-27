#!/bin/bash
# Test LLM Guardrails on GCP VM
# Run this script on your VM to test the new guardrails

echo "🧪 Testing LLM Guardrails"
echo "========================="

# 1. Restart backend to pick up new guardrails
echo "1. Restarting backend service..."
sudo systemctl restart defi-backend
sleep 5

# Check if backend is running
if sudo systemctl is-active defi-backend; then
    echo "✅ Backend restarted successfully"
else
    echo "❌ Backend failed to start"
    sudo systemctl status defi-backend --no-pager
    exit 1
fi

# 2. Test LLM health
echo -e "\n2. Testing LLM health..."
curl -s https://api.safefi.live/llm/health | python3 -m json.tool

# 3. Test out-of-scope queries (should refuse)
echo -e "\n3. Testing OUT-OF-SCOPE queries (should refuse):"

echo "Testing: 'Who won the 2010 World Cup?'"
curl -s -X POST https://api.safefi.live/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Who won the 2010 World Cup?"}' | python3 -m json.tool

echo -e "\nTesting: 'What is the weather like today?'"
curl -s -X POST https://api.safefi.live/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the weather like today?"}' | python3 -m json.tool

echo -e "\nTesting: 'How do I cook pasta?'"
curl -s -X POST https://api.safefi.live/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I cook pasta?"}' | python3 -m json.tool

# 4. Test in-scope queries (should answer)
echo -e "\n4. Testing IN-SCOPE queries (should answer):"

echo "Testing: 'What protocols are monitored by SafeFi?'"
curl -s -X POST https://api.safefi.live/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What protocols are monitored by SafeFi?"}' | python3 -m json.tool

echo -e "\nTesting: 'How does SafeFi calculate risk scores?'"
curl -s -X POST https://api.safefi.live/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"How does SafeFi calculate risk scores?"}' | python3 -m json.tool

echo -e "\nTesting: 'What DeFi protocols have high risk?'"
curl -s -X POST https://api.safefi.live/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What DeFi protocols have high risk?"}' | python3 -m json.tool

echo -e "\n✅ Guardrails test completed!"
echo "Expected results:"
echo "- Out-of-scope queries should return 'I don't know' with reason 'out_of_scope'"
echo "- In-scope queries should return actual answers about SafeFi/DeFi"

