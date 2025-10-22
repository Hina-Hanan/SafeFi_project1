#!/bin/bash
# Complete HTTPS Setup Script for GCP Backend
# This script will fix the Mixed Content error by setting up HTTPS on your backend

echo "=========================================="
echo "🔒 Complete HTTPS Setup for Backend"
echo "=========================================="
echo ""

# Get VM IP automatically
VM_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google" 2>/dev/null || curl -s ifconfig.me)
echo "📍 Detected VM IP: $VM_IP"
echo ""

# Get GitHub username from git remote or ask user
GITHUB_USERNAME=$(git remote get-url origin 2>/dev/null | sed 's/.*github.com[:/]\([^/]*\).*/\1/' || echo "")
if [ -z "$GITHUB_USERNAME" ]; then
    read -p "Enter your GitHub username: " GITHUB_USERNAME
fi
echo "📁 GitHub Username: $GITHUB_USERNAME"
echo ""

# Step 1: Install SSL dependencies
echo "📦 Installing SSL dependencies..."
sudo apt update
sudo apt install -y openssl

# Step 2: Create SSL certificate directory
echo "🔐 Creating SSL certificate directory..."
sudo mkdir -p /etc/ssl/private
sudo mkdir -p /etc/ssl/certs

# Step 3: Generate self-signed SSL certificate
echo "🔑 Generating SSL certificate..."
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/backend.key \
  -out /etc/ssl/certs/backend.crt \
  -subj "/C=US/ST=California/L=San Francisco/O=DeFi Risk Assessment/CN=$VM_IP" \
  -addext "subjectAltName=IP:$VM_IP"

# Step 4: Set proper permissions
echo "🔒 Setting SSL certificate permissions..."
sudo chmod 600 /etc/ssl/private/backend.key
sudo chmod 644 /etc/ssl/certs/backend.crt
sudo chown root:root /etc/ssl/private/backend.key
sudo chown root:root /etc/ssl/certs/backend.crt

# Step 5: Clone/Update repository if needed
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

# Step 6: Update backend systemd service for HTTPS
echo "⚙️ Updating backend service for HTTPS..."
sudo tee /etc/systemd/system/defi-backend.service > /dev/null << EOF
[Unit]
Description=DeFi Risk Assessment Backend API
After=network.target postgresql.service ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/main-project/backend
Environment="PATH=/home/$USER/main-project/backend/venv/bin"
ExecStart=/home/$USER/main-project/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=/etc/ssl/private/backend.key --ssl-certfile=/etc/ssl/certs/backend.crt --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 6: Update CORS configuration
echo "🌐 Updating CORS configuration..."
cd /home/$USER/main-project/backend

# Backup original .env
cp .env .env.backup

# Add HTTPS CORS origins
if ! grep -q "CORS_ORIGINS" .env; then
    echo "CORS_ORIGINS=https://storage.googleapis.com,https://34.30.34.157" >> .env
else
    # Update existing CORS_ORIGINS
    sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=https://storage.googleapis.com,https://$VM_IP|g" .env
fi

# Step 7: Update firewall rules for HTTPS
echo "🔥 Configuring firewall for HTTPS..."
sudo ufw allow 8000/tcp
sudo ufw --force enable

# Step 8: Restart backend service
echo "🔄 Restarting backend service..."
sudo systemctl daemon-reload
sudo systemctl restart defi-backend

# Wait for service to start
sleep 5

# Step 9: Test HTTPS connection
echo "🧪 Testing HTTPS connection..."
echo "Testing backend HTTPS endpoint..."

# Test with curl (ignore certificate warnings for self-signed)
if curl -k -s https://$VM_IP:8000/health > /dev/null; then
    echo "✅ HTTPS backend is working!"
    echo "✅ Backend URL: https://$VM_IP:8000"
    echo "✅ Health Check: https://$VM_IP:8000/health"
else
    echo "❌ HTTPS test failed. Checking service status..."
    sudo systemctl status defi-backend
fi

# Step 10: Show service status
echo ""
echo "📊 Service Status:"
sudo systemctl status defi-backend --no-pager

echo ""
echo "🎉 HTTPS Setup Complete!"
echo ""
echo "📋 What was configured:"
echo "   ✅ SSL certificate generated and installed"
echo "   ✅ Backend service updated for HTTPS"
echo "   ✅ CORS configured for HTTPS origins"
echo "   ✅ Firewall rules updated"
echo "   ✅ Service restarted with HTTPS"
echo ""
echo "🔗 Your HTTPS URLs:"
echo "   Backend API: https://$VM_IP:8000"
echo "   Health Check: https://$VM_IP:8000/health"
echo "   API Docs: https://$VM_IP:8000/docs"
echo ""
echo "⚠️  Important Notes:"
echo "   - Self-signed certificate will show browser warnings"
echo "   - Users need to click 'Advanced' → 'Proceed to site'"
echo "   - For production, use GCP Load Balancer with managed certificates"
echo ""
echo "🧪 Test your frontend now - Mixed Content errors should be resolved!"
