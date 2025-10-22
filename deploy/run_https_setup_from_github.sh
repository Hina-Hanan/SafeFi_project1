#!/bin/bash
# GitHub-based HTTPS Setup Script
# This script downloads and runs the HTTPS setup directly from GitHub

echo "=========================================="
echo "🔒 GitHub-based HTTPS Setup"
echo "=========================================="
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME
echo "📁 GitHub Username: $GITHUB_USERNAME"
echo ""

# Get VM IP
VM_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google" 2>/dev/null || curl -s ifconfig.me)
echo "📍 VM IP: $VM_IP"
echo ""

# Clone or update repository
echo "📥 Getting latest code from GitHub..."
if [ ! -d "/home/$USER/main-project" ]; then
    echo "📥 Cloning repository..."
    cd /home/$USER
    git clone https://github.com/$GITHUB_USERNAME/main-project.git
else
    echo "📥 Updating repository..."
    cd /home/$USER/main-project
    git pull origin main
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x deploy/setup_https_backend.sh
chmod +x deploy/rebuild_frontend_https.sh
chmod +x deploy/fix_mixed_content_complete.sh

# Run the master script
echo "🚀 Running HTTPS setup..."
./deploy/fix_mixed_content_complete.sh

echo ""
echo "🎉 HTTPS setup completed!"
echo "Your backend should now be accessible at: https://$VM_IP:8000"


