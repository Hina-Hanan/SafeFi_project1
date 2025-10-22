#!/bin/bash

# Deploy frontend with safefi.live domain configuration
# Run this script from your local machine

set -e

echo "🚀 Deploying frontend with safefi.live domain configuration..."

# Build frontend with production environment
echo "📦 Building frontend..."
cd frontend

# Create production environment file
cat > .env << 'EOF'
# API Base URL - Use the custom domain
VITE_API_BASE_URL=https://api.safefi.live

# Environment
VITE_ENVIRONMENT=production

# App Configuration
VITE_APP_NAME=SafeFi Risk Assessment
VITE_APP_VERSION=1.0.0

# Feature Flags
VITE_ENABLE_AI_ASSISTANT=true
VITE_ENABLE_EMAIL_ALERTS=true
VITE_ENABLE_RISK_NOTIFICATIONS=true
EOF

# Install dependencies and build
npm install
npm run build

echo "✅ Frontend built successfully!"

# Upload to Cloud Storage
echo "☁️ Uploading to Cloud Storage..."
gsutil -m cp -r dist/* gs://safefi-frontend/

# Set proper permissions for public access
gsutil -m acl ch -r -u AllUsers:R gs://safefi-frontend/

echo "✅ Frontend deployed successfully!"
echo "🌐 Your app is now available at: https://safefi.live"
echo "🔗 API is available at: https://api.safefi.live"

cd ..
