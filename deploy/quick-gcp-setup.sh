#!/bin/bash

# Quick GCP setup script for SafeFi
# Run this on your local machine to setup everything on GCP

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Quick GCP Setup for SafeFi${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install it first:${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Configuration
VM_NAME="safefi-production"
ZONE="us-central1-a"
MACHINE_TYPE="e2-medium"
PROJECT_ID=$(gcloud config get-value project)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ No GCP project selected${NC}"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${YELLOW}📍 Project: $PROJECT_ID${NC}"
echo ""

# Step 1: Create VM
echo -e "${YELLOW}Step 1: Creating VM instance...${NC}"
if gcloud compute instances describe $VM_NAME --zone=$ZONE &> /dev/null; then
    echo "VM already exists, skipping creation"
else
    gcloud compute instances create $VM_NAME \
        --zone=$ZONE \
        --machine-type=$MACHINE_TYPE \
        --image-family=ubuntu-2204-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=50GB \
        --boot-disk-type=pd-balanced \
        --tags=http-server,https-server,safefi-app
    
    echo -e "${GREEN}✅ VM created${NC}"
fi

# Step 2: Configure Firewall
echo ""
echo -e "${YELLOW}Step 2: Configuring firewall rules...${NC}"

# HTTP
if ! gcloud compute firewall-rules list --filter="name=allow-http" --format="value(name)" | grep -q "allow-http"; then
    gcloud compute firewall-rules create allow-http \
        --allow tcp:80 \
        --source-ranges 0.0.0.0/0 \
        --target-tags http-server \
        --description "Allow HTTP traffic for SafeFi"
    echo -e "${GREEN}✅ HTTP firewall rule created${NC}"
else
    echo "HTTP firewall rule already exists"
fi

# HTTPS
if ! gcloud compute firewall-rules list --filter="name=allow-https" --format="value(name)" | grep -q "allow-https"; then
    gcloud compute firewall-rules create allow-https \
        --allow tcp:443 \
        --source-ranges 0.0.0.0/0 \
        --target-tags https-server \
        --description "Allow HTTPS traffic for SafeFi"
    echo -e "${GREEN}✅ HTTPS firewall rule created${NC}"
else
    echo "HTTPS firewall rule already exists"
fi

# Step 3: Wait for VM to be ready
echo ""
echo -e "${YELLOW}Step 3: Waiting for VM to be ready...${NC}"
sleep 30

# Step 4: Setup VM
echo ""
echo -e "${YELLOW}Step 4: Setting up VM (this may take a few minutes)...${NC}"

gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    echo '📦 Installing Docker...'
    
    # Install Docker
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker \$USER
    fi
    
    # Install Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        sudo curl -L \"https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    # Install Git and other tools
    sudo apt-get update
    sudo apt-get install -y git curl wget nano
    
    # Install Nginx
    if ! command -v nginx &> /dev/null; then
        sudo apt-get install -y nginx
        sudo systemctl enable nginx
    fi
    
    # Install Certbot
    if ! command -v certbot &> /dev/null; then
        sudo apt-get install -y certbot python3-certbot-nginx
    fi
    
    echo '✅ Software installed'
"

echo -e "${GREEN}✅ VM setup completed${NC}"

# Step 5: Get VM IP
echo ""
echo -e "${YELLOW}Step 5: Getting VM IP address...${NC}"
VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo -e "${GREEN}📍 VM IP: $VM_IP${NC}"

# Step 6: Instructions
echo ""
echo -e "${GREEN}✅ GCP Setup Complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Point your domain to this IP address:"
echo "   safefi.live → $VM_IP"
echo "   api.safefi.live → $VM_IP"
echo ""
echo "2. Clone the repository on the VM:"
echo "   ssh $VM_NAME --zone=$ZONE"
echo "   cd /opt"
echo "   git clone https://github.com/your-username/safefi.git"
echo "   cd safefi/deploy"
echo ""
echo "3. Configure environment:"
echo "   nano .env.production"
echo ""
echo "4. Setup SSL certificates:"
echo "   sudo certbot --nginx -d safefi.live -d www.safefi.live"
echo "   sudo certbot --nginx -d api.safefi.live"
echo ""
echo "5. Deploy application:"
echo "   ./deploy.sh"
echo ""
echo "Or run the automated deployment:"
echo "   ./deploy-to-gcp.sh"
echo ""
echo -e "${GREEN}For detailed instructions, see: deploy/GCP_DEPLOYMENT_GUIDE.md${NC}"
