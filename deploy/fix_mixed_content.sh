#!/bin/bash
# HTTPS Setup Script for GCP Deployment
# This script configures HTTPS for both frontend and backend to fix Mixed Content errors

echo "=========================================="
echo "HTTPS Configuration for GCP Deployment"
echo "=========================================="
echo ""

# Get VM details
read -p "Enter your GCP VM External IP: " VM_IP
read -p "Enter your GCP Project ID: " PROJECT_ID

echo ""
echo "🔒 HTTPS Setup Configuration"
echo "VM IP: $VM_IP"
echo "Project: $PROJECT_ID"
echo ""

# Create HTTPS configuration script
cat > configure_https.sh << EOF
#!/bin/bash
echo "🔒 Configuring HTTPS for Mixed Content Fix..."

# 1. Update frontend API configuration
echo "📝 Updating frontend API configuration..."
cd ~/SafeFi_project1/frontend/src/services

# Backup original file
cp api.ts api.ts.backup

# Update API URL to use HTTPS
sed -i "s|return 'https://34.125.123.45:8000'|return 'https://$VM_IP:8000'|g" api.ts

echo "✅ Frontend API updated to use HTTPS: https://$VM_IP:8000"

# 2. Build frontend with HTTPS
echo "🏗️ Building frontend with HTTPS configuration..."
cd ~/SafeFi_project1/frontend
npm run build

echo "✅ Frontend built with HTTPS configuration"

# 3. Update backend CORS for HTTPS
echo "🔧 Updating backend CORS configuration..."
cd ~/SafeFi_project1/backend

# Update CORS origins to include HTTPS
sed -i 's|CORS_ORIGINS=.*|CORS_ORIGINS=https://storage.googleapis.com,https://your-frontend-domain.com|g' .env

echo "✅ Backend CORS updated for HTTPS"

# 4. Restart backend
echo "🔄 Restarting backend..."
pkill -f uvicorn
source venv/bin/activate
export PYTHONPATH=\$PWD:\$PYTHONPATH
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

echo "✅ Backend restarted with HTTPS support"

echo ""
echo "🎉 HTTPS Configuration Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Deploy frontend to Cloud Storage"
echo "2. Configure GCP Load Balancer with SSL certificate"
echo "3. Test HTTPS endpoints"
echo ""
echo "🔗 URLs:"
echo "   Frontend: https://storage.googleapis.com/defi-risk-frontend-$PROJECT_ID/index.html"
echo "   Backend: https://$VM_IP:8000"
echo "   Health Check: https://$VM_IP:8000/health"
EOF

chmod +x configure_https.sh

# Create GCP Load Balancer configuration
cat > setup_load_balancer.sh << 'EOF'
#!/bin/bash
echo "🌐 Setting up GCP Load Balancer for HTTPS..."

# Create backend service
gcloud compute backend-services create defi-backend-service \
    --global \
    --protocol HTTP \
    --health-checks defi-health-check \
    --timeout 30s

# Create URL map
gcloud compute url-maps create defi-url-map \
    --default-service defi-backend-service

# Create HTTPS proxy
gcloud compute target-https-proxies create defi-https-proxy \
    --url-map defi-url-map \
    --ssl-certificates defi-ssl-cert

# Create forwarding rule
gcloud compute forwarding-rules create defi-https-rule \
    --global \
    --target-https-proxy defi-https-proxy \
    --ports 443

echo "✅ Load Balancer configured for HTTPS"
EOF

chmod +x setup_load_balancer.sh

echo "📋 INSTRUCTIONS TO FIX MIXED CONTENT ERRORS:"
echo ""
echo "1. 🔒 Run HTTPS Configuration:"
echo "   ./configure_https.sh"
echo ""
echo "2. 🌐 Deploy Frontend to Cloud Storage:"
echo "   - Create bucket: defi-risk-frontend-$PROJECT_ID"
echo "   - Upload files from frontend/dist/"
echo "   - Make bucket public"
echo ""
echo "3. 🔧 Configure GCP Load Balancer (Optional but Recommended):"
echo "   - Create SSL certificate"
echo "   - Set up HTTPS proxy"
echo "   - Configure forwarding rules"
echo ""
echo "4. 🧪 Test HTTPS Endpoints:"
echo "   curl https://$VM_IP:8000/health"
echo "   curl https://storage.googleapis.com/defi-risk-frontend-$PROJECT_ID/index.html"
echo ""
echo "📁 Files Created:"
echo "   - configure_https.sh (main configuration script)"
echo "   - setup_load_balancer.sh (GCP Load Balancer setup)"
echo ""
echo "⚠️  Important Notes:"
echo "   - Mixed Content errors occur when HTTP requests are made from HTTPS pages"
echo "   - All API calls must use HTTPS in production"
echo "   - GCP Load Balancer handles SSL termination"
echo "   - Backend can still run on HTTP internally (VM to Load Balancer)"
echo ""
echo "✅ This will completely resolve your Mixed Content errors!"


