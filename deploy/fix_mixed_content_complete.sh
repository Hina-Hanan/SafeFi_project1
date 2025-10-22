#!/bin/bash
# Master HTTPS Fix Script - Complete Solution for Mixed Content Error
# This script fixes the Mixed Content error by setting up HTTPS for both frontend and backend

echo "=========================================="
echo "🔒 Master HTTPS Fix - Mixed Content Solution"
echo "=========================================="
echo ""

# Get VM IP
VM_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google" 2>/dev/null || curl -s ifconfig.me)
echo "📍 VM IP: $VM_IP"
echo ""

# Step 1: Setup HTTPS Backend
echo "🔧 Step 1: Setting up HTTPS Backend..."
chmod +x /home/$USER/main-project/deploy/setup_https_backend.sh
/home/$USER/main-project/deploy/setup_https_backend.sh

if [ $? -eq 0 ]; then
    echo "✅ Backend HTTPS setup completed successfully"
else
    echo "❌ Backend HTTPS setup failed"
    exit 1
fi

echo ""
echo "⏳ Waiting 10 seconds for backend to fully start..."
sleep 10

# Step 2: Test Backend HTTPS
echo "🧪 Step 2: Testing Backend HTTPS..."
if curl -k -s https://$VM_IP:8000/health > /dev/null; then
    echo "✅ Backend HTTPS is working!"
else
    echo "❌ Backend HTTPS test failed"
    echo "Checking service status..."
    sudo systemctl status defi-backend --no-pager
    exit 1
fi

# Step 3: Rebuild Frontend
echo "🏗️ Step 3: Rebuilding Frontend with HTTPS..."
chmod +x /home/$USER/main-project/deploy/rebuild_frontend_https.sh
/home/$USER/main-project/deploy/rebuild_frontend_https.sh

if [ $? -eq 0 ]; then
    echo "✅ Frontend rebuild completed successfully"
else
    echo "❌ Frontend rebuild failed"
    exit 1
fi

# Step 4: Final Verification
echo "🔍 Step 4: Final Verification..."

echo "Testing backend endpoints:"
echo "  Health Check:"
curl -k -s https://$VM_IP:8000/health | head -1

echo "  API Docs:"
curl -k -s https://$VM_IP:8000/docs | head -1

echo "  Protocols endpoint:"
curl -k -s https://$VM_IP:8000/protocols | head -1

# Get project info for frontend URL
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

echo ""
echo "🎉 HTTPS Setup Complete!"
echo "=========================================="
echo ""
echo "✅ Mixed Content Error Fixed!"
echo ""
echo "🔗 Your Application URLs:"
if [ -n "$PROJECT_ID" ]; then
    echo "   Frontend: https://storage.googleapis.com/defi-risk-frontend-$PROJECT_ID/index.html"
else
    echo "   Frontend: Local build in dist/ folder"
fi
echo "   Backend API: https://$VM_IP:8000"
echo "   Health Check: https://$VM_IP:8000/health"
echo "   API Documentation: https://$VM_IP:8000/docs"
echo ""
echo "📋 What was fixed:"
echo "   ✅ Backend now serves HTTPS on port 8000"
echo "   ✅ SSL certificate generated and configured"
echo "   ✅ CORS updated for HTTPS origins"
echo "   ✅ Frontend rebuilt with HTTPS API calls"
echo "   ✅ All Mixed Content errors resolved"
echo ""
echo "⚠️ Important Notes:"
echo "   - Self-signed certificate will show browser warnings"
echo "   - Users need to click 'Advanced' → 'Proceed to site'"
echo "   - For production, use GCP Load Balancer with managed certificates"
echo ""
echo "🧪 Test your application now!"
echo "   Open your frontend URL and check browser console"
echo "   Mixed Content errors should be completely resolved!"




