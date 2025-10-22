#!/bin/bash
# Frontend HTTPS Rebuild Script
# This script rebuilds the frontend with HTTPS configuration

echo "=========================================="
echo "🏗️ Frontend HTTPS Rebuild"
echo "=========================================="
echo ""

# Get VM IP
VM_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google" 2>/dev/null || curl -s ifconfig.me)
echo "📍 VM IP: $VM_IP"
echo ""

# Get GitHub username from git remote or ask user
GITHUB_USERNAME=$(git remote get-url origin 2>/dev/null | sed 's/.*github.com[:/]\([^/]*\).*/\1/' || echo "")
if [ -z "$GITHUB_USERNAME" ]; then
    read -p "Enter your GitHub username: " GITHUB_USERNAME
fi
echo "📁 GitHub Username: $GITHUB_USERNAME"
echo ""

# Ensure repository is available
echo "📁 Ensuring repository is available..."
if [ ! -d "/home/$USER/main-project" ]; then
    echo "📥 Cloning repository from GitHub..."
    cd /home/$USER
    git clone https://github.com/$GITHUB_USERNAME/main-project.git
else
    echo "📥 Updating repository from GitHub..."
    cd /home/$USER/main-project
    git pull origin main
fi

# Navigate to frontend directory
cd /home/$USER/main-project/frontend

# Step 1: Verify API configuration
echo "📝 Checking API configuration..."
if grep -q "https://$VM_IP:8000" src/services/api.ts; then
    echo "✅ API already configured for HTTPS"
else
    echo "🔧 Updating API configuration for HTTPS..."
    sed -i "s|http://$VM_IP:8000|https://$VM_IP:8000|g" src/services/api.ts
    echo "✅ API updated to use HTTPS"
fi

# Step 2: Install dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Step 3: Build frontend
echo "🏗️ Building frontend..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend built successfully"
else
    echo "❌ Frontend build failed"
    exit 1
fi

# Step 4: Deploy to Cloud Storage (if configured)
echo "☁️ Deploying to Cloud Storage..."
if command -v gsutil &> /dev/null; then
    # Get project ID
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -n "$PROJECT_ID" ]; then
        BUCKET_NAME="defi-risk-frontend-$PROJECT_ID"
        echo "📤 Uploading to bucket: $BUCKET_NAME"
        
        # Create bucket if it doesn't exist
        gsutil mb gs://$BUCKET_NAME 2>/dev/null || true
        
        # Upload files
        gsutil -m cp -r dist/* gs://$BUCKET_NAME/
        
        # Make bucket public
        gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
        
        echo "✅ Frontend deployed to: https://storage.googleapis.com/$BUCKET_NAME/index.html"
    else
        echo "⚠️ GCP project not configured. Frontend built locally in dist/ folder"
    fi
else
    echo "⚠️ gsutil not found. Frontend built locally in dist/ folder"
fi

echo ""
echo "🎉 Frontend HTTPS Rebuild Complete!"
echo ""
echo "📋 What was done:"
echo "   ✅ API configuration verified for HTTPS"
echo "   ✅ Frontend dependencies installed"
echo "   ✅ Frontend built with HTTPS configuration"
echo "   ✅ Deployed to Cloud Storage (if available)"
echo ""
echo "🔗 Your Frontend URL:"
if [ -n "$PROJECT_ID" ]; then
    echo "   https://storage.googleapis.com/defi-risk-frontend-$PROJECT_ID/index.html"
else
    echo "   Local build available in: dist/ folder"
fi
echo ""
echo "🧪 Test your application now!"
echo "   - Frontend: https://storage.googleapis.com/defi-risk-frontend-$PROJECT_ID/index.html"
echo "   - Backend: https://$VM_IP:8000"
echo "   - Mixed Content errors should be resolved!"
