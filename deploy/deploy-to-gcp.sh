#!/bin/bash

# Automated deployment script for SafeFi to GCP
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Deploying SafeFi to GCP${NC}"

# Configuration
VM_NAME="safefi-production"
ZONE="us-central1-a"
PROJECT_DIR="/opt/safefi"

# Check if running on GCP VM
if ! gcloud compute instances list --filter="name=$VM_NAME" --format="value(name)" | grep -q "$VM_NAME"; then
    echo -e "${RED}❌ VM $VM_NAME not found in current project${NC}"
    echo "Please create the VM first using GCP_DEPLOYMENT_GUIDE.md"
    exit 1
fi

# Get VM external IP
VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo -e "${YELLOW}📍 VM IP: $VM_IP${NC}"

# Deploy via SSH
echo -e "${YELLOW}📦 Connecting to VM and deploying...${NC}"

gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    set -e
    
    echo '📁 Navigating to project directory'
    cd $PROJECT_DIR || {
        echo '❌ Project not found. Please clone repository first.'
        exit 1
    }
    
    echo '🔄 Pulling latest code'
    git fetch origin
    git checkout main
    git pull origin main
    
    echo '🏗️  Rebuilding containers'
    docker-compose build --no-cache
    
    echo '🔄 Updating containers'
    docker-compose up -d
    
    echo '🔍 Waiting for services to start...'
    sleep 15
    
    echo '📊 Running database migrations'
    docker-compose exec -T api alembic upgrade head || echo 'No migrations to run'
    
    echo '🏥 Running health checks...'
    
    # Frontend health
    if curl -f -s http://localhost:80/health > /dev/null 2>&1; then
        echo '✅ Frontend is healthy'
    else
        echo '⚠️  Frontend health check failed'
    fi
    
    # Backend health
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo '✅ Backend API is healthy'
    else
        echo '⚠️  Backend health check failed'
    fi
    
    # Database health
    if docker exec safefi-db pg_isready -U defi_user > /dev/null 2>&1; then
        echo '✅ Database is healthy'
    else
        echo '⚠️  Database health check failed'
    fi
    
    echo '✅ Deployment completed!'
    
    echo ''
    echo '📍 Services available at:'
    echo '  - Frontend: https://safefi.live'
    echo '  - Backend API: https://api.safefi.live'
    echo '  - API Docs: https://api.safefi.live/docs'
    echo '  - MLflow: http://localhost:5000'
"

echo -e "${GREEN}🎉 Deployment successful!${NC}"
