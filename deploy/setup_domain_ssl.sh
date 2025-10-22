#!/bin/bash

# Setup SSL Certificate for safefi.live domain
# Run this script on your VM after DNS propagation (wait 10-15 minutes after DNS changes)

set -e

echo "🔐 Setting up SSL certificate for safefi.live domain..."

# Update system packages
sudo apt update

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Stop Nginx temporarily
sudo systemctl stop nginx

# Generate SSL certificate for safefi.live and www.safefi.live
echo "📋 Generating SSL certificate..."
sudo certbot certonly --standalone \
    --email hinahanan2003@gmail.com \
    --agree-tos \
    --no-eff-email \
    -d safefi.live \
    -d www.safefi.live \
    -d api.safefi.live

# Create certificate directory for Nginx
sudo mkdir -p /etc/ssl/safefi.live

# Copy certificates to Nginx directory
sudo cp /etc/letsencrypt/live/safefi.live/fullchain.pem /etc/ssl/safefi.live/
sudo cp /etc/letsencrypt/live/safefi.live/privkey.pem /etc/ssl/safefi.live/

# Set proper permissions
sudo chmod 644 /etc/ssl/safefi.live/fullchain.pem
sudo chmod 600 /etc/ssl/safefi.live/privkey.pem

echo "✅ SSL certificates generated successfully!"
echo "📁 Certificates stored in: /etc/ssl/safefi.live/"

# Test certificate renewal
echo "🔄 Testing certificate renewal..."
sudo certbot renew --dry-run

echo "✅ SSL setup complete!"
echo "🔗 Your domain will be available at: https://safefi.live"
echo "🔗 API will be available at: https://api.safefi.live"
