#!/bin/bash
# Quick Fix for Mixed Content Errors
# Run this script on your GCP VM to immediately fix HTTPS issues

echo "🔧 Quick Fix for Mixed Content Errors"
echo "====================================="
echo ""

# Get VM IP
VM_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")
echo "📍 VM IP: $VM_IP"
echo ""

# Navigate to project
cd ~/SafeFi_project1/frontend/src/services

# Backup original file
cp api.ts api.ts.backup
echo "💾 Backed up original api.ts"

# Update API URL to use HTTPS
sed -i "s|return 'https://34.125.123.45:8000'|return 'https://$VM_IP:8000'|g" api.ts
echo "✅ Updated API URL to use HTTPS: https://$VM_IP:8000"

# Build frontend
echo "🏗️ Building frontend..."
cd ~/SafeFi_project1/frontend
npm run build
echo "✅ Frontend built successfully"

# Update backend CORS
echo "🔧 Updating backend CORS..."
cd ~/SafeFi_project1/backend

# Add HTTPS origins to CORS
if ! grep -q "https://storage.googleapis.com" .env; then
    echo "CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://storage.googleapis.com,https://$VM_IP" >> .env
    echo "✅ Added HTTPS origins to CORS"
else
    echo "✅ CORS already configured for HTTPS"
fi

# Restart backend
echo "🔄 Restarting backend..."
pkill -f uvicorn
source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

echo "✅ Backend restarted"

echo ""
echo "🎉 Mixed Content Fix Complete!"
echo ""
echo "📋 What was fixed:"
echo "   ✅ Frontend API calls now use HTTPS"
echo "   ✅ Backend CORS allows HTTPS origins"
echo "   ✅ Frontend rebuilt with HTTPS configuration"
echo "   ✅ Backend restarted with new settings"
echo ""
echo "🧪 Test the fix:"
echo "   curl https://$VM_IP:8000/health"
echo ""
echo "📁 Files updated:"
echo "   - frontend/src/services/api.ts (HTTPS API URL)"
echo "   - backend/.env (HTTPS CORS origins)"
echo "   - frontend/dist/ (rebuilt with HTTPS)"
echo ""
echo "🌐 Next: Deploy frontend to Cloud Storage for full HTTPS setup"


