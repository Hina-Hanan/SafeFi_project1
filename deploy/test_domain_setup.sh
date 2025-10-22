#!/bin/bash

# Test safefi.live domain setup
# Run this script to verify everything is working

set -e

echo "🧪 Testing safefi.live domain setup..."
echo "======================================"

# Test DNS resolution
echo "🔍 Testing DNS resolution..."
echo "Testing safefi.live..."
nslookup safefi.live
echo ""
echo "Testing www.safefi.live..."
nslookup www.safefi.live
echo ""
echo "Testing api.safefi.live..."
nslookup api.safefi.live

# Test HTTPS connectivity
echo ""
echo "🔐 Testing HTTPS connectivity..."

echo "Testing https://safefi.live..."
curl -I https://safefi.live || echo "❌ safefi.live not accessible"

echo ""
echo "Testing https://www.safefi.live..."
curl -I https://www.safefi.live || echo "❌ www.safefi.live not accessible"

echo ""
echo "Testing https://api.safefi.live/health..."
curl -I https://api.safefi.live/health || echo "❌ API not accessible"

# Test SSL certificate
echo ""
echo "🔒 Testing SSL certificate..."
echo | openssl s_client -servername safefi.live -connect safefi.live:443 2>/dev/null | openssl x509 -noout -dates

# Test backend services
echo ""
echo "🔧 Testing backend services..."
echo "PostgreSQL status:"
sudo systemctl is-active postgresql

echo "Ollama status:"
sudo systemctl is-active ollama

echo "FastAPI backend status:"
sudo systemctl is-active defi-backend

echo "Nginx status:"
sudo systemctl is-active nginx

# Test API endpoints
echo ""
echo "🌐 Testing API endpoints..."
echo "Health endpoint:"
curl -s https://api.safefi.live/health | jq . || echo "❌ Health endpoint failed"

echo ""
echo "Protocols endpoint:"
curl -s https://api.safefi.live/protocols | jq . || echo "❌ Protocols endpoint failed"

echo ""
echo "LLM health endpoint:"
curl -s https://api.safefi.live/llm/health | jq . || echo "❌ LLM endpoint failed"

echo ""
echo "✅ Domain testing completed!"
echo "🌐 Your app should be accessible at: https://safefi.live"
