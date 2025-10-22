#!/bin/bash
# GCP Deployment Script - Phase 3: Frontend Deployment
# This script helps deploy the frontend to Cloud Storage

echo "=========================================="
echo "Phase 3: Frontend Deployment"
echo "=========================================="
echo ""

# Get VM details
read -p "Enter your GCP VM External IP: " VM_IP
read -p "Enter your GCP Project ID: " PROJECT_ID

echo ""
echo "🌐 Frontend Deployment Setup"
echo "VM IP: $VM_IP"
echo "Project: $PROJECT_ID"
echo ""

# Create frontend update script
cat > update_frontend_api.js << EOF
// Update frontend API URL for production
const fs = require('fs');
const path = require('path');

const apiFile = path.join(__dirname, 'src', 'services', 'api.ts');
let content = fs.readFileSync(apiFile, 'utf8');

// Replace API URL
content = content.replace(
  /return 'https:\/\/34\.125\.123\.45:8000'/,
  "return 'https://$VM_IP:8000'"
);

fs.writeFileSync(apiFile, content);
console.log('✅ Updated API URL to:', 'https://$VM_IP:8000');
EOF

# Create build script
cat > build_frontend.sh << 'EOF'
#!/bin/bash
echo "🔧 Building frontend for production..."

# Update API URL
node update_frontend_api.js

# Install dependencies
npm install

# Build for production
npm run build

echo "✅ Frontend built successfully!"
echo "📁 Files ready in: dist/"
EOF

chmod +x build_frontend.sh

echo "📋 INSTRUCTIONS:"
echo ""
echo "1. 🏗️ Create VM Instance (if not done):"
echo "   - Go to: Compute Engine → VM instances → CREATE INSTANCE"
echo "   - Name: defi-backend-vm"
echo "   - Region: us-central1 (Iowa)"
echo "   - Zone: us-central1-a"
echo "   - Machine type: e2-medium (2 vCPU, 4 GB memory)"
echo "   - Boot disk: Ubuntu 22.04 LTS, 40 GB"
echo "   - Firewall: ✅ Allow HTTP traffic, ✅ Allow HTTPS traffic"
echo "   - Click CREATE"
echo ""

echo "2. 🔧 Setup Backend VM:"
echo "   - SSH into your VM"
echo "   - Run: curl -fsSL https://raw.githubusercontent.com/$GITHUB_USERNAME/main-project/main/deploy/vm_setup.sh | bash"
echo "   - Wait 15-20 minutes for complete setup"
echo ""

echo "3. 🌐 Create Cloud Storage Bucket:"
echo "   - Go to: Cloud Storage → Buckets → CREATE"
echo "   - Name: defi-risk-frontend-$PROJECT_ID"
echo "   - Location: Region → us-central1"
echo "   - Storage class: Standard"
echo "   - Access control: Fine-grained"
echo "   - Click CREATE"
echo ""

echo "4. 📦 Build Frontend (on your local machine):"
echo "   cd frontend"
echo "   # Copy the generated files to frontend directory"
echo "   cp ../deploy/update_frontend_api.js ."
echo "   cp ../deploy/build_frontend.sh ."
echo "   ./build_frontend.sh"
echo ""

echo "5. 📤 Upload to Cloud Storage:"
echo "   - Open your bucket in GCP Console"
echo "   - UPLOAD FILES → Select all files from frontend/dist/"
echo "   - Wait for upload to complete"
echo ""

echo "6. 🌍 Make Bucket Public:"
echo "   - Go to PERMISSIONS tab"
echo "   - ADD PRINCIPAL → allUsers"
echo "   - Role: Storage Object Viewer"
echo "   - SAVE → ALLOW PUBLIC ACCESS"
echo ""

echo "7. 🔗 Get Frontend URL:"
echo "   - Click on index.html in your bucket"
echo "   - Copy the Public URL"
echo "   - Format: https://storage.googleapis.com/defi-risk-frontend-$PROJECT_ID/index.html"
echo ""

echo "⏱️ Expected time: 20-30 minutes"
echo "📊 Monitor progress in GCP Console"
echo ""
echo "✅ Next: Phase 4 - CORS Configuration"

# Create CORS update script for later
cat > update_cors.sh << 'EOF'
#!/bin/bash
# CORS Update Script - Run this on the VM after frontend is deployed

read -p "Enter your frontend URL (from Cloud Storage): " FRONTEND_URL

echo "🔧 Updating CORS configuration..."

cd ~/main-project/backend
source venv/bin/activate

# Update CORS in main.py
sed -i "s|allow_origins=\[.*\]|allow_origins=[\"http://localhost:5173\", \"https://storage.googleapis.com\", \"$FRONTEND_URL\"]|g" app/main.py

# Restart backend
sudo systemctl restart defi-backend

echo "✅ CORS updated!"
echo "🌐 Frontend URL: $FRONTEND_URL"
echo "🔗 Backend URL: http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google"):8000"
EOF

chmod +x update_cors.sh

echo ""
echo "📁 Files created:"
echo "   - update_frontend_api.js (for building)"
echo "   - build_frontend.sh (build script)"
echo "   - update_cors.sh (for Phase 4)"


