#!/bin/bash

# Complete safefi.live domain setup script
# Run this script on your VM after DNS propagation (wait 10-15 minutes after DNS changes)

set -e

echo "🌐 Setting up safefi.live domain for SafeFi Risk Assessment..."
echo "================================================================"

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root. Run as postgres user."
    exit 1
fi

# Get current external IP
echo "🔍 Getting current external IP..."
CURRENT_IP=$(curl -s ifconfig.me)
echo "📍 Current external IP: $CURRENT_IP"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Install Certbot
echo "🔐 Installing Certbot for SSL certificates..."
sudo apt install -y certbot python3-certbot-nginx

# Stop Nginx temporarily
echo "⏸️ Stopping Nginx..."
sudo systemctl stop nginx

# Generate SSL certificate for safefi.live
echo "📋 Generating SSL certificate for safefi.live..."
sudo certbot certonly --standalone \
    --email hinahanan2003@gmail.com \
    --agree-tos \
    --no-eff-email \
    -d safefi.live \
    -d www.safefi.live \
    -d api.safefi.live

# Create certificate directory for Nginx
echo "📁 Setting up certificate directory..."
sudo mkdir -p /etc/ssl/safefi.live

# Copy certificates to Nginx directory
sudo cp /etc/letsencrypt/live/safefi.live/fullchain.pem /etc/ssl/safefi.live/
sudo cp /etc/letsencrypt/live/safefi.live/privkey.pem /etc/ssl/safefi.live/

# Set proper permissions
sudo chmod 644 /etc/ssl/safefi.live/fullchain.pem
sudo chmod 600 /etc/ssl/safefi.live/privkey.pem

echo "✅ SSL certificates generated successfully!"

# Apply Nginx configuration
echo "🔧 Applying Nginx configuration for safefi.live..."

# Copy the new configuration
sudo cp /var/lib/postgresql/SafeFi_project1/deploy/nginx_safefi_config.conf /etc/nginx/sites-available/safefi.live

# Remove old configuration
sudo rm -f /etc/nginx/sites-available/defi-backend
sudo rm -f /etc/nginx/sites-enabled/defi-backend

# Enable new configuration
sudo ln -sf /etc/nginx/sites-available/safefi.live /etc/nginx/sites-enabled/

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid!"
    
    # Start Nginx
    echo "🔄 Starting Nginx..."
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    echo "✅ Nginx started successfully!"
else
    echo "❌ Nginx configuration test failed!"
    exit 1
fi

# Test certificate renewal
echo "🔄 Testing certificate renewal..."
sudo certbot renew --dry-run

# Set up automatic certificate renewal
echo "⏰ Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

echo ""
echo "🎉 Domain setup completed successfully!"
echo "================================================================"
echo "🌐 Your SafeFi Risk Assessment app is now available at:"
echo "   - Frontend: https://safefi.live"
echo "   - API: https://api.safefi.live"
echo "   - www: https://www.safefi.live"
echo ""
echo "🔐 SSL certificates are automatically renewed"
echo "📱 Your app is now mobile-friendly with HTTPS"
echo "🌍 Professional domain name for your DeFi risk assessment platform"
echo ""
echo "📋 Next steps:"
echo "   1. Deploy your frontend with the new domain configuration"
echo "   2. Test all functionality on your mobile device"
echo "   3. Share your professional URL: https://safefi.live"
